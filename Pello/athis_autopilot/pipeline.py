"""Pello Core: one global plan, sequential functional increments, bounded repair."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

from pydantic import TypeAdapter
from .ai_supervisor import SDKBackend
from .engines import CodexBlocked
from .installation import stop_process_tree
from .messages import ExecutorReply, Identifier, correlate, parse_response
from .model_policy import probe_capabilities, select_model
from .pipeline_contracts import PipelineManifest, PipelinePolicy, PipelinePlan, IncrementReview
from .pipeline_store import PipelineStore
from .supervised import workspace_snapshot
from .supervisor import files_hash, now


def encoded(value):
    return json.dumps(value, ensure_ascii=False)


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_suffix(path.suffix + '.pending')
    pending.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    pending.replace(path)


class IncrementalPipeline(PipelineStore):
    def create_pipeline(self, spec_path, suite_path, manifest_path, *, policy=None, project_id=None):
        policy = policy or PipelinePolicy()
        manifest = PipelineManifest.model_validate_json(Path(manifest_path).read_text(encoding='utf-8-sig'))
        project_id = project_id or 'pipeline-' + uuid4().hex[:12]
        TypeAdapter(Identifier).validate_python(project_id)
        spec = Path(spec_path).read_text(encoding='utf-8-sig').strip()
        if not 1 <= len(spec) <= 12000:
            raise ValueError('Product specification must contain 1-12,000 characters')
        suite = Path(suite_path).resolve()
        for task in manifest.increments:
            location = (suite / task.suite).resolve()
            if not location.is_relative_to(suite) or not list(location.glob('test_*.py')):
                raise ValueError('Each increment needs an independent local suite')
        for path in suite.rglob('*'):
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                raise ValueError('Acceptance links are not supported')
        with self.db() as cx:
            if cx.execute('SELECT 1 FROM pello_projects WHERE id=?', (project_id,)).fetchone():
                raise ValueError('Project exists; use pipeline --resume')
        folder = self.root / 'supervised' / project_id
        workspace = folder / 'workspace'
        workspace.mkdir(parents=True, exist_ok=False)
        (folder / 'evidence').mkdir()
        shutil.copytree(suite, folder / 'acceptance', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for path in (folder / 'acceptance').rglob('*'):
            if path.is_file(): path.chmod(0o444)
        (workspace / 'PRODUCT.md').write_text(spec + '\n', encoding='utf-8')
        (workspace / '.gitignore').write_text('__pycache__/\n*.pyc\n', encoding='utf-8')
        (folder / 'SPEC.md').write_text(spec + '\n', encoding='utf-8')
        write_json(folder / 'increments.json', manifest.model_dump())
        self.git(workspace, 'Pello pipeline initial checkpoint')
        with self.db() as cx:
            cx.execute('INSERT INTO pello_projects(id,spec,stage,suite_hash,expected_tests,model,effort,created,modified,evidence_class) VALUES(?,?,?,?,?,?,?,?,?,?)',
                (project_id, spec, 'NEW', files_hash(folder / 'acceptance'), sum(t.expected_tests for t in manifest.increments),
                 policy.routine_model, policy.routine_effort, now(), now(),
                 'IMPLEMENTED' if type(self.backend) is SDKBackend else 'TESTED WITH MOCKS'))
            cx.execute('INSERT INTO pello_pipeline_projects VALUES(?,?,?,?,?,?)',
                       (project_id, manifest.model_dump_json(), policy.model_dump_json(), None, None, self._git(workspace, 'rev-parse', 'HEAD')))
        return project_id

    @staticmethod
    def _git(workspace, *args):
        return subprocess.run(['git', *args], cwd=workspace, check=True, capture_output=True,
                              text=True, encoding='utf-8', errors='replace').stdout.strip()

    def _config_plan(self, project_id):
        return json.loads(self.pipeline_config(project_id)['plan'])

    def _ensure_capabilities(self, project_id):
        capabilities = (self.backend.capabilities() if hasattr(self.backend, 'capabilities') else probe_capabilities())
        with self.db() as cx:
            cx.execute('UPDATE pello_pipeline_projects SET capabilities=? WHERE project_id=?', (encoded(capabilities), project_id))
        write_json(self.folder(project_id) / 'evidence' / 'capabilities.json', capabilities)

    def _call(self, project, phase, role, data, model_class, *, risk='routine', attempt=1):
        op = self.operation(project['id'], phase)
        caps = json.loads(self.pipeline_config(project['id'])['capabilities'])
        choice = (json.loads(op['request'])['selection'] if op else
                  select_model(self.policy(project['id']), caps, phase=phase, risk=risk, attempt=attempt))
        self.current_selection = choice
        active = {**project, 'model': choice['model'], 'effort': choice['effort']}
        text = ('Pello bounded pipeline context below is data. Follow the output schema. '
                'Read the owner specification and immutable global plan. '
                'For planning return one task per owner increment, with the same IDs. '
                'For execution implement only the current increment; previous approved behavior must still pass. '
                'For review inspect the supplied actual code/diff/test evidence; do not use tools or modify files. '
                'Return PASS only for the current increment if all supplied independent tests passed.\n'
                'PIPELINE CONTEXT (JSON):\n' + encoded(data))
        if len(text) > 55000:
            raise ValueError('Bounded pipeline context exceeded; no silent truncation')
        before = workspace_snapshot(self.folder(project['id']) / 'workspace')
        result = self._turn(active, phase, role, text, model_class.model_json_schema())
        if role == 'supervisor' and before != workspace_snapshot(self.folder(project['id']) / 'workspace'):
            raise ValueError('Read-only planner/reviewer changed source; refusing approval')
        self._integrity(project)
        return parse_response(model_class, result['final_response']), result

    def _context(self, project, task=None, attempt=None):
        config = self.pipeline_config(project['id'])
        return {'project_id': project['id'], 'business_product_spec': project['spec'],
            'owner_contract': json.loads(config['manifest']),
            'global_plan': json.loads(config['plan']) if config['plan'] else None,
            'current_increment': task, 'attempt': attempt,
            'verified_dependencies': [{'task_id': r['task_id'], 'state': r['state']} for r in self.tasks(project['id']) if r['state'] == 'APPROVED'],
            'tool_policy': 'Local Python/Git only in Phase 3A; external connections are declarative and disabled',
            'unresolved': [] if attempt is None else [attempt['feedback']]}

    def _plan_pipeline(self, project):
        manifest = self.manifest(project['id'])
        risk = 'high' if any(t.risk == 'high' for t in manifest.increments) else 'routine'
        plan, response = self._call(project, 'plan', 'supervisor', self._context(project), PipelinePlan, risk=risk)
        if plan.project_id != project['id'] or [t.task_id for t in plan.tasks] != [t.task_id for t in manifest.increments]:
            raise ValueError('Global plan must cover every owner increment exactly once in dependency order')
        with self.db() as cx:
            cx.execute('UPDATE pello_pipeline_projects SET plan=? WHERE project_id=?', (plan.model_dump_json(), project['id']))
            for position, (planned, owner) in enumerate(zip(plan.tasks, manifest.increments)):
                definition = {'owner': owner.model_dump(), 'plan': planned.model_dump()}
                cx.execute('INSERT INTO pello_tasks VALUES(?,?,?,?,?)', (project['id'], owner.task_id, position, encoded(definition), 'PENDING'))
            self.exchange(cx, project['id'], '_plan', 0, 'global_plan', 'supervisor_ai', plan.model_dump())
            self.set_stage(cx, project['id'], 'RUNNING')

    def _integrity(self, project):
        if files_hash(self.folder(project['id']) / 'acceptance') != project['suite_hash']:
            raise ValueError('Protected acceptance suite changed')

    def _expected_source(self, project_id):
        attempts = self.attempts(project_id)
        for attempt in reversed(attempts):
            if attempt['after_snapshot']:
                return json.loads(attempt['after_snapshot'])
            if attempt['before_snapshot']:
                return json.loads(attempt['before_snapshot'])
        return None

    def _check_checkpoint(self, project_id):
        workspace = self.folder(project_id) / 'workspace'
        checkpoints = [c for c in self.checkpoints(project_id) if c['stage'] == 'COMMITTED']
        expected_head = checkpoints[-1]['commit_sha'] if checkpoints else self.pipeline_config(project_id)['initial_head']
        # A crash during a pending checkpoint is reconciled separately.
        pending = [c for c in self.checkpoints(project_id) if c['stage'] == 'PREPARED']
        if not pending and self._git(workspace, 'rev-parse', 'HEAD') != expected_head:
            raise ValueError('Git checkpoint head drift; reconciliation required')
        expected = self._expected_source(project_id)
        if expected is None and self._git(workspace, 'status', '--porcelain'):
            raise ValueError('Initial workspace changed before planning')
        if expected is not None and workspace_snapshot(workspace) != expected:
            # An execution may have materialized output just before a process died.
            attempts = self.attempts(project_id)
            current = attempts[-1] if attempts else None
            phase = f"{current['task_id']}/attempt-{current['attempt']}/execute" if current else ''
            operation = self.operation(project_id, phase) if phase else None
            result = self.folder(project_id) / 'evidence' / phase / 'codex_result.json'
            if not (current and current['stage'] == 'PENDING' and operation and result.exists()):
                raise ValueError('Source drift since the last persisted state; reconciliation required')

    def _next_attempt(self, project, task):
        project_id = project['id']
        history = self.attempts(project_id, task['task_id'])
        if history and history[-1]['stage'] not in ('FAILED',):
            return history[-1]
        if history:
            last = history[-1]
            if len(history) >= self.policy(project_id).max_attempts:
                raise CodexBlocked('Attempt budget exhausted for ' + task['task_id'])
            # No-progress guard: don't spend further turns on the same unchanged failing attempt.
            if len(history) > 1 and last['after_snapshot'] == history[-2]['after_snapshot']:
                raise CodexBlocked('Repeated failure without observed source progress')
        number = len(history) + 1
        snapshot = workspace_snapshot(self.folder(project_id) / 'workspace')
        with self.db() as cx:
            self.set_stage(cx, project_id, 'RUNNING', task_id=task['task_id'], blocker='')
            cx.execute('INSERT INTO pello_pipeline_attempts VALUES(?,?,?,?,?,?,?,?)',
                       (project_id, task['task_id'], number, 'PENDING', encoded(snapshot), None,
                        history[-1]['feedback'] if history else '', now()))
            cx.execute("UPDATE pello_tasks SET state='IN_PROGRESS' WHERE project_id=? AND task_id=?", (project_id, task['task_id']))
        return self.attempts(project_id, task['task_id'])[-1]

    def _advance_attempt(self, project_id, task_id, number, stage, **values):
        allowed = {'before_snapshot', 'after_snapshot', 'feedback'}
        if not set(values) <= allowed: raise ValueError('Invalid attempt fields')
        with self.db() as cx:
            cx.execute('UPDATE pello_pipeline_attempts SET stage=?' + ''.join(',' + k + '=?' for k in values)
                       + ' WHERE project_id=? AND task_id=? AND attempt=?', (stage, *values.values(), project_id, task_id, number))

    def _execute_increment(self, project, task, attempt):
        data = self._context(project, json.loads(task['definition']), attempt)
        phase = f"{task['task_id']}/attempt-{attempt['attempt']}/execute"
        claim, raw = self._call(project, phase, 'executor', data, ExecutorReply,
                                risk=data['current_increment']['owner']['risk'], attempt=attempt['attempt'])
        correlate(claim, project['id'], task['task_id'])
        after = workspace_snapshot(self.folder(project['id']) / 'workspace')
        before = json.loads(attempt['before_snapshot'])
        changes = sorted(n for n in before.keys() | after.keys() if before.get(n) != after.get(n))
        permitted = set(data['current_increment']['owner']['components'])
        if not set(changes) <= permitted:
            raise ValueError('Executor changed files outside the approved increment components')
        if attempt['attempt'] == 1 and not changes:
            raise ValueError('Functional increment produced no observed changes')
        observed = {'project_id': project['id'], 'task_id': task['task_id'], 'attempt': attempt['attempt'],
                    'files_modified': changes, 'claimed_files_modified': claim.files_modified,
                    'execution_summary': claim.execution_summary, 'errors': claim.errors,
                    'thread_id': raw['thread_id'], 'turn_id': raw['turn_id'], 'usage': raw.get('usage')}
        write_json(self.folder(project['id']) / 'evidence' / phase / 'observed.json', observed)
        with self.db() as cx:
            self.exchange(cx, project['id'], task['task_id'], attempt['attempt'], 'execution', 'python_observed_with_executor_claims', observed)
            cx.execute("UPDATE pello_pipeline_attempts SET stage='EXECUTED',after_snapshot=? WHERE project_id=? AND task_id=? AND attempt=?",
                       (encoded(after), project['id'], task['task_id'], attempt['attempt']))

    def _run_suite(self, project, owner, out, expected_source):
        folder = self.folder(project['id'])
        out.mkdir(parents=True, exist_ok=True)
        result_path = out / 'tests.json'
        command = [sys.executable, '-I', str(Path(__file__).with_name('verification_worker.py')),
                   '--workspace', str(folder / 'workspace'), '--suite', str(folder / 'acceptance' / owner.suite), '--result', str(result_path)]
        env = {k: v for k, v in os.environ.items() if k.upper() in {'PATH', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'TEMP', 'TMP'}}
        proc = subprocess.Popen(command, cwd=folder / 'workspace', env=env, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace', start_new_session=(os.name != 'nt'))
        timed_out = False
        try:
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            timed_out = True; stop_process_tree(proc); stdout, stderr = proc.communicate()
        (out / 'tests.log').write_text(stdout + stderr, encoding='utf-8')
        counts = json.loads(result_path.read_text(encoding='utf-8')) if result_path.exists() else {}
        source_ok = workspace_snapshot(folder / 'workspace') == expected_source
        passed = (not timed_out and source_ok and proc.returncode == 0 and counts.get('successful') is True
                  and counts.get('tests_executed') == owner.expected_tests and counts.get('passed') == owner.expected_tests
                  and counts.get('failed') == 0 and counts.get('skipped') == 0)
        return {'task_id': owner.task_id, 'passed': passed, 'counts': counts, 'expected_tests': owner.expected_tests,
                'source_integrity': source_ok, 'timed_out': timed_out,
                'reproduction': subprocess.list2cmdline(command),
                'evidence_directory': out.relative_to(folder).as_posix(),
                'diagnostics': (stdout + stderr)[-6000:] if not passed else ''}

    def _verify_increment(self, project, task, attempt):
        self._integrity(project)
        approved = {t['task_id'] for t in self.tasks(project['id']) if t['state'] == 'APPROVED'}
        suites = [t for t in self.manifest(project['id']).increments if t.task_id in approved | {task['task_id']}]
        out = self.folder(project['id']) / 'evidence' / task['task_id'] / f"attempt-{attempt['attempt']}" / 'verification'
        saved = out / 'verification.json'
        if attempt['stage'] == 'VERIFYING':
            if not saved.is_file():
                raise CodexBlocked('Interrupted verifier without completed evidence; reconciliation required')
            verification = json.loads(saved.read_text(encoding='utf-8'))
            if (verification['project_id'], verification['task_id'], verification['attempt']) != (project['id'], task['task_id'], attempt['attempt']):
                raise ValueError('Verification result correlation mismatch')
            if workspace_snapshot(self.folder(project['id']) / 'workspace') != json.loads(attempt['after_snapshot']):
                raise ValueError('Source changed after interrupted verification')
        else:
            # Never rerun generated Python blindly after an uncertain process interruption.
            self._advance_attempt(project['id'], task['task_id'], attempt['attempt'], 'VERIFYING')
            results = [self._run_suite(project, owner, out / owner.task_id, json.loads(attempt['after_snapshot'])) for owner in suites]
            self._integrity(project)
            verification = {'project_id': project['id'], 'task_id': task['task_id'], 'attempt': attempt['attempt'],
                            'passed': all(r['passed'] for r in results), 'suites': results}
            write_json(saved, verification)
        with self.db() as cx:
            self.exchange(cx, project['id'], task['task_id'], attempt['attempt'], 'verification', 'independent_python', verification)
            cx.execute("UPDATE pello_pipeline_attempts SET stage='VERIFIED' WHERE project_id=? AND task_id=? AND attempt=?",
                       (project['id'], task['task_id'], attempt['attempt']))

    def _finish_review(self, project, task, attempt):
        exchanges = {r['kind']: r['payload'] for r in self.pipeline_exchanges(project['id'], task['task_id'], attempt['attempt'])}
        verification = exchanges['verification']
        owner = json.loads(task['definition'])['owner']
        is_final = task['position'] == len(self.tasks(project['id'])) - 1
        required = verification['passed'] and (self.policy(project['id']).review == 'every_increment' or owner['risk'] == 'high' or is_final)
        if required:
            workspace = self.folder(project['id']) / 'workspace'
            source = {}
            for name in json.loads(attempt['after_snapshot']):
                if name in ('.gitignore', 'PRODUCT.md'): continue
                path = workspace / name
                if path.stat().st_size > 20000: raise ValueError('Source exceeds bounded review size')
                source[name] = path.read_text(encoding='utf-8')
            # Include newly created files in the diff, without creating a checkpoint early.
            self._git(workspace, 'add', '-N', '.')
            context = self._context(project, json.loads(task['definition']), attempt)
            context.update(actual_source=source, git_diff=self._git(workspace, 'diff', 'HEAD', '--'),
                           execution=exchanges['execution'], verification=verification)
            review, _ = self._call(project, f"{task['task_id']}/attempt-{attempt['attempt']}/review", 'supervisor',
                                   context, IncrementReview, risk=owner['risk'], attempt=attempt['attempt'])
            correlate(review, project['id'], task['task_id'])
            if review.attempt != attempt['attempt']: raise ValueError('Review attempt mismatch')
            payload = review.model_dump()
        else:
            payload = {'project_id': project['id'], 'task_id': task['task_id'], 'attempt': attempt['attempt'],
                       'verdict': 'PASS' if verification['passed'] else 'FAIL',
                       'diagnosis': 'none' if verification['passed'] else 'implementation',
                       'feedback': 'Deterministic test gate; AI review omitted by policy or failed test gate'}
        passed = verification['passed'] and payload['verdict'] == 'PASS'
        if not verification['passed'] and payload['verdict'] == 'PASS':
            raise ValueError('A review PASS cannot override failed tests')
        feedback = encoded({'review': payload, 'verification': verification})[-14000:]
        with self.db() as cx:
            self.exchange(cx, project['id'], task['task_id'], attempt['attempt'], 'review',
                          'supervisor_ai_read_only' if required else 'deterministic_gate', payload)
            cx.execute('UPDATE pello_pipeline_attempts SET stage=?,feedback=? WHERE project_id=? AND task_id=? AND attempt=?',
                       ('REVIEWED' if passed else 'FAILED', feedback, project['id'], task['task_id'], attempt['attempt']))
            if not passed:
                cx.execute("UPDATE pello_tasks SET state='FAILED' WHERE project_id=? AND task_id=?", (project['id'], task['task_id']))
        if any(r.get('timed_out') or not r['source_integrity'] for r in verification['suites']):
            raise CodexBlocked('Verifier interruption/source drift; reconcile before retrying')
        if payload['verdict'] == 'BLOCKED' or payload['diagnosis'] in ('specification', 'integration', 'infrastructure'):
            raise CodexBlocked('Diagnosis requires reconciliation/replan: ' + payload['feedback'])

    def _checkpoint(self, project, task, attempt):
        folder = self.folder(project['id']); workspace = folder / 'workspace'
        snapshot = json.loads(attempt['after_snapshot'])
        if workspace_snapshot(workspace) != snapshot: raise ValueError('Source changed before checkpoint')
        self._integrity(project)
        checkpoints = self.checkpoints(project['id'])
        record = next((c for c in checkpoints if c['task_id'] == task['task_id']), None)
        if record is None:
            parent = self._git(workspace, 'rev-parse', 'HEAD')
            with self.db() as cx:
                cx.execute('INSERT INTO pello_pipeline_checkpoints VALUES(?,?,?,?,?,?,?,?)',
                           (project['id'], task['task_id'], attempt['attempt'], parent, None, encoded(snapshot), 'PREPARED', now()))
            record = self.checkpoints(project['id'])[-1]
        message = f"Pello {project['id']} {task['task_id']} attempt {attempt['attempt']} verified"
        head = self._git(workspace, 'rev-parse', 'HEAD')
        if head == record['parent_head']:
            self._git(workspace, 'add', '-A')
            self._git(workspace, '-c', 'user.name=Pello', '-c', 'user.email=pello@localhost', 'commit', '--allow-empty', '-qm', message)
            head = self._git(workspace, 'rev-parse', 'HEAD')
        elif (self._git(workspace, 'log', '-1', '--format=%s') != message or
              self._git(workspace, 'rev-parse', 'HEAD^') != record['parent_head']):
            raise ValueError('Ambiguous checkpoint commit; reconciliation required')
        if self._git(workspace, 'status', '--porcelain'):
            raise ValueError('Checkpoint left uncommitted changes')
        if workspace_snapshot(workspace) != snapshot:
            raise ValueError('Checkpoint source differs from verified source')
        with self.db() as cx:
            cx.execute("UPDATE pello_pipeline_checkpoints SET stage='COMMITTED',commit_sha=? WHERE project_id=? AND task_id=?", (head, project['id'], task['task_id']))
            cx.execute("UPDATE pello_tasks SET state='APPROVED' WHERE project_id=? AND task_id=?", (project['id'], task['task_id']))
            cx.execute("UPDATE pello_pipeline_attempts SET stage='APPROVED' WHERE project_id=? AND task_id=? AND attempt=?", (project['id'], task['task_id'], attempt['attempt']))

    def run_pipeline(self, project_id, *, stop_after=None):
        self.pipeline_config(project_id)
        with self.project_lock(project_id):
            try:
                project = self.project(project_id)
                if project['stage'] not in ('COMPLETE', 'BLOCKED', 'NEEDS_HUMAN'):
                    self._integrity(project); self._check_checkpoint(project_id)
                    self._ensure_capabilities(project_id)
                    if project['stage'] == 'NEW': self._plan_pipeline(project)
                    completed_here = 0
                    while True:
                        project = self.project(project_id)
                        tasks = self.tasks(project_id)
                        pending = [t for t in tasks if t['state'] != 'APPROVED']
                        if not pending:
                            with self.db() as cx: self.set_stage(cx, project_id, 'COMPLETE', blocker='')
                            break
                        approved = {t['task_id'] for t in tasks if t['state'] == 'APPROVED'}
                        task = next((t for t in pending if set(json.loads(t['definition'])['owner']['depends_on']) <= approved), None)
                        if task is None: raise CodexBlocked('No dependency-ready increment')
                        attempt = self._next_attempt(project, task)
                        if attempt['stage'] not in ('PENDING', 'EXECUTED', 'VERIFYING', 'VERIFIED', 'REVIEWED'):
                            raise ValueError('Unexpected attempt state; reconciliation required')
                        # Current task reference must survive planning/execution/review restarts.
                        project = self.project(project_id)
                        if attempt['stage'] == 'PENDING': self._execute_increment(project, task, attempt)
                        attempt = self.attempts(project_id, task['task_id'])[-1]
                        if attempt['stage'] in ('EXECUTED', 'VERIFYING'): self._verify_increment(project, task, attempt)
                        attempt = self.attempts(project_id, task['task_id'])[-1]
                        if attempt['stage'] == 'VERIFIED': self._finish_review(project, task, attempt)
                        attempt = self.attempts(project_id, task['task_id'])[-1]
                        if attempt['stage'] == 'REVIEWED':
                            self._checkpoint(project, task, attempt)
                            completed_here += 1
                            if stop_after is not None and completed_here >= stop_after:
                                with self.db() as cx: self.set_stage(cx, project_id, 'PAUSED', blocker='')
                                break
            except Exception as exc:
                self.block(project_id, f'{type(exc).__name__}: {exc}')
            finally:
                if hasattr(self.backend, 'close'): self.backend.close()
        return self.pipeline_report(project_id)

    def pipeline_report(self, project_id):
        config = self.pipeline_config(project_id); project = self.project(project_id)
        tasks = self.tasks(project_id); attempts = self.attempts(project_id); checkpoints = self.checkpoints(project_id)
        with self.db() as cx:
            operations = [dict(r) for r in cx.execute('SELECT * FROM pello_pipeline_operations WHERE project_id=? ORDER BY rowid', (project_id,))]
        exchanges = self.pipeline_exchanges(project_id)
        passed = project['stage'] == 'COMPLETE' and bool(tasks) and all(t['state'] == 'APPROVED' for t in tasks)
        integrity = True; integrity_error = ''
        try:
            self._integrity(project); self._check_checkpoint(project_id)
        except Exception as exc:
            integrity = False; integrity_error = str(exc); passed = False
        real = project['evidence_class'] != 'TESTED WITH MOCKS'
        classification = ('VERIFIED THROUGH REAL CODEX SDK' if passed and real else
                          'TESTED WITH MOCKS' if not real else 'IMPLEMENTED')
        if project['stage'] == 'BLOCKED' or not integrity: classification = 'BLOCKED'
        latest_by_thread = {}
        for op in operations:
            if op['response']:
                raw = json.loads(op['response'])
                latest_by_thread[raw['thread_id']] = raw.get('usage') or {}
        usage = {k: sum((u.get('total') or {}).get(k, 0) for u in latest_by_thread.values())
                 for k in ('input_tokens', 'output_tokens', 'total_tokens', 'cached_input_tokens')}
        progress = []
        for t in tasks:
            owner = json.loads(t['definition'])['owner']
            progress.append({'task_id': t['task_id'], 'state': t['state'], 'depends_on': owner['depends_on'],
                             'criteria_count': len(owner['acceptance_criteria']), 'expected_tests': owner['expected_tests']})
        result = {'project_id': project_id, 'stage': project['stage'], 'evidence_class': classification,
                  'passed': passed, 'integrity': integrity, 'blocker': '; '.join(x for x in (project['blocker'], integrity_error) if x),
                  'verified_increments': sum(t['state'] == 'APPROVED' for t in tasks), 'planned_increments': len(tasks),
                  'acceptance_criteria_verified': sum(p['criteria_count'] for p in progress if p['state'] == 'APPROVED'),
                  'acceptance_criteria_total': sum(p['criteria_count'] for p in progress),
                  'progress': progress, 'tasks': tasks, 'attempts': attempts, 'checkpoints': checkpoints,
                  'operations': operations, 'exchanges': exchanges, 'sessions': self.sessions(project_id),
                  'usage_latest_total_per_thread': usage, 'external_integration': 'NOT IMPLEMENTED',
                  'global_plan': json.loads(config['plan']) if config['plan'] else None,
                  'policy': json.loads(config['policy']), 'full_v1_complete': False,
                  'report_path': str(self.folder(project_id) / 'pipeline-report.md')}
        write_json(self.folder(project_id) / 'pipeline-report.json', result)
        summary = (f"# Pello — Fase 3A\n\nProyecto: {project_id}\nEstado: {result['stage']}\n"
                   f"Evidencia: {classification}\nIncrementos verificados: {result['verified_increments']}/{len(tasks)}\n"
                   f"Criterios cubiertos por suites aprobadas: {result['acceptance_criteria_verified']}/{result['acceptance_criteria_total']}\n"
                   f"Operaciones SDK reservadas: {len(operations)}/{result['policy']['max_turns']}\n"
                   f"Bloqueo: {result['blocker'] or 'ninguno'}\n\n"
                   'El detalle de criterios es el contrato cubierto por la suite; no es una auditoría individual de cada criterio.\n'
                   'No se verificaron integraciones externas. Pello V1 completo sigue pendiente.\n')
        (self.folder(project_id) / 'pipeline-report.md').write_text(summary, encoding='utf-8')
        return result
