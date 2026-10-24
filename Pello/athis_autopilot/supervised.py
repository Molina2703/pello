"""Phase 2: one plan -> execution -> verification -> review cycle, no retries."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4

from .ai_supervisor import SDKBackend, context_prompt
from .bridge import Bridge
from .engines import CodexBlocked
from .installation import stop_process_tree
from .messages import (ExecutionResult, ExecutorReply, Identifier, SupervisorDecision,
                       TaskDefinition, VerificationResult, correlate, parse_response)
from .supervisor import files_hash, now

FINAL_STAGES = {'REVIEWED', 'BLOCKED', 'NEEDS_HUMAN'}


def workspace_snapshot(workspace):
    result = {}
    for path in sorted(workspace.rglob('*')):
        if '.git' in path.relative_to(workspace).parts or '__pycache__' in path.parts:
            continue
        if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
            raise ValueError('Workspace links are not supported')
        if path.is_file():
            if path.stat().st_size > 1_000_000 or len(result) >= 100:
                raise ValueError('Phase 2 workspace size limit exceeded')
            result[path.relative_to(workspace).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


class SupervisedCycle(Bridge):
    def __init__(self, root, backend=None, timeout=180):
        super().__init__(root)
        self.backend = backend if backend is not None else SDKBackend()
        if not 1 <= timeout <= 900:
            raise ValueError('Turn timeout must be 1-900 seconds')
        self.timeout = timeout

    def create_supervised(self, spec_path, suite_path, *, model='gpt-6-luna', effort='low', project_id=None):
        from pydantic import TypeAdapter
        project_id = project_id or 'phase2-' + uuid4().hex[:12]
        TypeAdapter(Identifier).validate_python(project_id)
        if effort not in ('low', 'medium'):
            raise ValueError('Phase 2 permits only low/medium reasoning, without escalation')
        spec = Path(spec_path).read_text(encoding='utf-8-sig').strip()
        if not spec or len(spec) > 12000:
            raise ValueError('Markdown product specification must contain 1-12,000 characters')
        suite_path = Path(suite_path).resolve()
        if not list(suite_path.glob('test_*.py')):
            raise ValueError('Independent acceptance suite required')
        manifest = json.loads((suite_path / 'manifest.json').read_text(encoding='utf-8'))
        expected = manifest['expected_tests']
        if type(expected) is not int or expected < 1:
            raise ValueError('manifest.json must declare a positive expected_tests count')
        # Check for ID reuse before any filesystem effects.
        with self.db() as cx:
            if cx.execute('SELECT 1 FROM pello_projects WHERE id=?', (project_id,)).fetchone():
                raise ValueError('Project ID exists; use supervised --resume to avoid duplicate work')
        folder = self.root / 'supervised' / project_id
        folder.mkdir(parents=True, exist_ok=False)
        workspace = folder / 'workspace'
        workspace.mkdir()
        (folder / 'evidence').mkdir()
        shutil.copytree(suite_path, folder / 'acceptance', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for path in (folder / 'acceptance').rglob('*'):
            if path.is_file():
                path.chmod(0o444)
        (workspace / 'PRODUCT.md').write_text(spec + '\n', encoding='utf-8')
        (workspace / '.gitignore').write_text('__pycache__/\n*.pyc\n', encoding='utf-8')
        self.git(workspace, 'Pello supervised project initial checkpoint')
        (folder / 'SPEC.md').write_text(spec + '\n', encoding='utf-8')
        with self.db() as cx:
            cx.execute('INSERT INTO pello_projects(id,spec,stage,suite_hash,expected_tests,model,effort,created,modified,evidence_class) VALUES(?,?,?,?,?,?,?,?,?,?)',
                       (project_id, spec, 'NEW', files_hash(folder / 'acceptance'), expected,
                        model, effort, now(), now(),
                        'IMPLEMENTED / UNVERIFIED' if type(self.backend) is SDKBackend else 'MOCK VERIFIED'))
        return project_id

    def _session(self, project, role):
        project_id = project['id']
        folder = self.folder(project_id)
        existing = next((x for x in self.sessions(project_id) if x['role'] == role), None)
        thread_file = folder / (role + '-thread.txt')
        if existing:
            if not thread_file.exists() or thread_file.read_text().strip() != existing['thread_id']:
                raise ValueError('Session file/database mismatch; reconciliation required')
            return existing
        ready = self.backend.prepare(workspace=folder / 'workspace', thread_file=thread_file,
                                     out_dir=folder / 'evidence' / (role + '-session'), role=role,
                                     model=project['model'], effort=project['effort'])
        if ready.get('status') != 'ready' or not ready.get('thread_id'):
            raise ValueError('Invalid session initialization result')
        if not thread_file.exists() or thread_file.read_text().strip() != ready['thread_id']:
            raise ValueError('Session initialization did not persist the expected identifier')
        with self.db() as cx:
            cx.execute('INSERT INTO pello_sessions VALUES(?,?,?,?,?,?,?)',
                       (project_id, role, ready['thread_id'], now(), None, project['task_id'], 'READY'))
        return next(x for x in self.sessions(project_id) if x['role'] == role)

    def _turn(self, project, phase, role, prompt, schema):
        project_id = project['id']
        folder = self.folder(project_id)
        operation = self.operation(project_id, phase)
        if operation:
            if operation['status'] == 'COMPLETED':
                response = json.loads(operation['response'])
            else:
                # A crash after SDK output but before SQLite commit can be reconciled
                # from this exact operation's saved result, without another model call.
                result_path = folder / 'evidence' / phase / 'codex_result.json'
                if not result_path.is_file():
                    raise CodexBlocked('Unresolved in-flight ' + phase + ' operation; reconcile effects before retrying')
                response = json.loads(result_path.read_text(encoding='utf-8'))
        else:
            session = self._session(project, role)
            self.reserve(project_id, phase, {'role': role, 'thread_id': session['thread_id'],
                                            'prompt': prompt, 'schema': schema})
            with self.db() as cx:
                cx.execute("UPDATE pello_sessions SET status='IN_FLIGHT',task_id=? WHERE project_id=? AND role=?",
                           (project['task_id'], project_id, role))
            response = self.backend.run(workspace=folder / 'workspace', thread_file=folder / (role + '-thread.txt'),
                                        out_dir=folder / 'evidence' / phase, role=role,
                                        model=project['model'], effort=project['effort'], prompt=prompt,
                                        schema=schema, timeout=self.timeout)
        session = next(x for x in self.sessions(project_id) if x['role'] == role)
        if response.get('status') != 'completed' or response.get('thread_id') != session['thread_id'] or not response.get('turn_id'):
            raise ValueError('SDK result is incomplete or belongs to the wrong role/session')
        self.save_response(project_id, phase, response)
        with self.db() as cx:
            cx.execute("UPDATE pello_sessions SET status='READY',last_successful_turn=? WHERE project_id=? AND role=?",
                       (response['turn_id'], project_id, role))
        return response

    def _plan(self, project):
        response = self._turn(project, 'plan', 'supervisor', context_prompt(project, 'plan'), SupervisorDecision.model_json_schema())
        decision = parse_response(SupervisorDecision, response['final_response'])
        correlate(decision, project['id'])
        if decision.decision not in ('CONTINUE', 'BLOCKED', 'NEEDS_HUMAN'):
            raise ValueError('Initial decision must select work or explain a blocker')
        if decision.decision == 'CONTINUE':
            if not decision.tasks or decision.task_id != decision.tasks[0].task_id or decision.tasks[0].depends_on:
                raise ValueError('Supervisor must select the first executable task')
        with self.db() as cx:
            self.add_exchange(cx, project['id'], decision.task_id, 'planning_decision', 'supervisor_ai', decision.model_dump())
            for position, task in enumerate(decision.tasks):
                cx.execute('INSERT INTO pello_tasks VALUES(?,?,?,?,?)',
                           (project['id'], task.task_id, position, task.model_dump_json(), 'PENDING'))
            self.set_stage(cx, project['id'], 'PLANNED' if decision.decision == 'CONTINUE' else decision.decision,
                           task_id=decision.task_id, blocker='' if decision.decision == 'CONTINUE' else decision.reasoning_summary)

    def _task(self, project):
        row = next(x for x in self.tasks(project['id']) if x['task_id'] == project['task_id'])
        return parse_response(TaskDefinition, row['definition'])

    def _execute(self, project):
        task = self._task(project)
        folder = self.folder(project['id'])
        before_path = folder / 'evidence' / 'before-execution.json'
        if not before_path.exists():
            before_path.write_text(json.dumps(workspace_snapshot(folder / 'workspace'), indent=2), encoding='utf-8')
        before = json.loads(before_path.read_text(encoding='utf-8'))
        response = self._turn(project, 'execute', 'executor',
                              context_prompt(project, 'execute', task=task.model_dump()), ExecutorReply.model_json_schema())
        claim = parse_response(ExecutorReply, response['final_response'])
        correlate(claim, project['id'], task.task_id)
        after = workspace_snapshot(folder / 'workspace')
        changes = sorted(name for name in before.keys() | after.keys() if before.get(name) != after.get(name))
        (folder / 'evidence' / 'after-execution.json').write_text(json.dumps(after, indent=2), encoding='utf-8')
        observed = ExecutionResult(project_id=project['id'], task_id=task.task_id,
                                   executor_session_id=response['thread_id'], execution_status='completed',
                                   files_modified=changes, claimed_files_modified=claim.files_modified,
                                   execution_summary=claim.execution_summary, errors=claim.errors,
                                   evidence_paths=['evidence/execute/codex_result.json', 'evidence/after-execution.json'],
                                   usage_metadata=response.get('usage') or {})
        with self.db() as cx:
            self.add_exchange(cx, project['id'], task.task_id, 'execution_result', 'python_observed_with_executor_claims', observed.model_dump())
            cx.execute("UPDATE pello_tasks SET state='EXECUTED' WHERE project_id=? AND task_id=? AND state='PENDING'", (project['id'], task.task_id))
            self.set_stage(cx, project['id'], 'EXECUTED')

    def _verify(self, project):
        folder = self.folder(project['id'])
        acceptance = folder / 'acceptance'
        if files_hash(acceptance) != project['suite_hash']:
            raise ValueError('Acceptance suite integrity failure')
        out = folder / 'evidence' / 'verification'
        out.mkdir(exist_ok=True)
        result_file = out / 'tests.json'
        log_file = out / 'tests.log'
        command = [sys.executable, '-I', str(Path(__file__).with_name('verification_worker.py')),
                   '--workspace', str(folder / 'workspace'), '--suite', str(acceptance), '--result', str(result_file)]
        permitted = {'PATH', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'TEMP', 'TMP'}
        env = {k: v for k, v in os.environ.items() if k.upper() in permitted}
        proc = subprocess.Popen(command, cwd=folder / 'workspace', env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                                encoding='utf-8', errors='replace', start_new_session=(os.name != 'nt'))
        timed_out = False
        try:
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            timed_out = True
            stop_process_tree(proc)
            stdout, stderr = proc.communicate()
        log_file.write_text(stdout + stderr, encoding='utf-8')
        if files_hash(acceptance) != project['suite_hash']:
            raise ValueError('Acceptance suite changed during verification')
        observed_source = json.loads((folder / 'evidence' / 'after-execution.json').read_text(encoding='utf-8'))
        source_unchanged = workspace_snapshot(folder / 'workspace') == observed_source
        counts = json.loads(result_file.read_text()) if result_file.exists() else {
            'tests_executed': 0, 'passed': 0, 'failed': 0, 'skipped': 0}
        passed = (source_unchanged and not timed_out and proc.returncode == 0 and counts.get('successful') is True
                  and counts['tests_executed'] == project['expected_tests']
                  and counts['passed'] == project['expected_tests'] and not counts['failed'] and not counts['skipped'])
        verification = VerificationResult(project_id=project['id'], task_id=project['task_id'],
            verification_status='PASSED' if passed else 'FAILED',
            tests_executed=counts['tests_executed'], passed=counts['passed'], failed=counts['failed'], skipped=counts['skipped'],
            evidence_paths=['evidence/verification/tests.json', 'evidence/verification/tests.log'],
            error_summary='' if passed else ('Verification timed out; reconcile process effects. ' if timed_out else '')
                + ('Workspace changed during verification. ' if not source_unchanged else '') + (stdout + stderr)[-8000:])
        with self.db() as cx:
            self.add_exchange(cx, project['id'], project['task_id'], 'verification_result', 'independent_local_verifier', verification.model_dump())
            cx.execute('UPDATE pello_tasks SET state=? WHERE project_id=? AND task_id=?',
                       ('VERIFIED' if passed else 'FAILED', project['id'], project['task_id']))
            self.set_stage(cx, project['id'], 'VERIFIED')

    def _review(self, project):
        exchanges = {x['kind']: x['payload'] for x in self.exchanges(project['id'])}
        response = self._turn(project, 'review', 'supervisor', context_prompt(project, 'review',
            task=self._task(project).model_dump(), execution=exchanges['execution_result'],
            verification=exchanges['verification_result'],
            tasks=[{'task_id': row['task_id'], 'state': row['state']} for row in self.tasks(project['id'])]),
            SupervisorDecision.model_json_schema())
        decision = parse_response(SupervisorDecision, response['final_response'])
        correlate(decision, project['id'], project['task_id'])
        if decision.tasks:
            raise ValueError('Review cannot replace the stored plan')
        all_verified = all(row['state'] == 'VERIFIED' for row in self.tasks(project['id']))
        with self.db() as cx:
            self.add_exchange(cx, project['id'], project['task_id'], 'review_decision', 'supervisor_ai', decision.model_dump())
            if decision.decision == 'COMPLETE' and not all_verified:
                self.set_stage(cx, project['id'], 'NEEDS_HUMAN', blocker='Python rejected false COMPLETE: required work is not independently verified')
            elif decision.decision == 'CONTINUE' and exchanges['verification_result']['verification_status'] != 'PASSED':
                self.set_stage(cx, project['id'], 'NEEDS_HUMAN', blocker='Python rejected CONTINUE after failed verification')
            else:
                self.set_stage(cx, project['id'], 'REVIEWED')

    def run_supervised(self, project_id):
        try:
            # A fixed finite state sequence; each SDK phase has a unique durable reservation.
            for stage, action in (('NEW', self._plan), ('PLANNED', self._execute),
                                  ('EXECUTED', self._verify), ('VERIFIED', self._review)):
                project = self.project(project_id)
                if project['stage'] == stage:
                    action(project)
        except Exception as exc:
            self.block(project_id, f'{type(exc).__name__}: {exc}')
        return self.supervised_report(project_id)

    def supervised_report(self, project_id):
        project = self.project(project_id)
        folder = self.folder(project_id)
        exchanges = self.exchanges(project_id)
        payloads = {item['kind']: item['payload'] for item in exchanges}
        with self.db() as cx:
            operations = [dict(x) for x in cx.execute('SELECT phase,status,created,modified FROM pello_operations WHERE project_id=? ORDER BY created', (project_id,))]
        sessions = self.sessions(project_id)
        verification = payloads.get('verification_result')
        decision = payloads.get('review_decision')
        cycle_finished = project['stage'] == 'REVIEWED' and decision is not None
        bridge_verified = bool(cycle_finished and verification and verification['tests_executed'] > 0
                               and len(operations) == 3 and all(x['status'] == 'COMPLETED' for x in operations)
                               and len(sessions) == 2 and len({x['thread_id'] for x in sessions}) == 2
                               and all(x['last_successful_turn'] for x in sessions))
        passed = bool(cycle_finished and verification and verification['verification_status'] == 'PASSED'
                      and decision['decision'] in ('COMPLETE', 'CONTINUE'))
        evidence_class = ('MOCK VERIFIED' if project['evidence_class'] == 'MOCK VERIFIED'
                          else ('REAL SDK VERIFIED' if bridge_verified else 'IMPLEMENTED / UNVERIFIED'))
        result = {'project_id': project_id, 'task_id': project['task_id'], 'stage': project['stage'],
                  'model': project['model'], 'effort': project['effort'], 'evidence_class': evidence_class,
                  'cycle_finished': cycle_finished, 'bridge_cycle_verified': bridge_verified,
                  'passed': passed, 'blocker': project['blocker'],
                  'sdk_turns_reserved': len(operations), 'operations': operations,
                  'supervisor_decision': decision, 'execution': payloads.get('execution_result'),
                  'verification': verification, 'tasks': self.tasks(project_id), 'sessions': sessions,
                  'exchanges': exchanges, 'suite_integrity': files_hash(folder / 'acceptance') == project['suite_hash'],
                  'report_path': str(folder / 'report.md'), 'evidence_directory': str(folder / 'evidence')}
        snapshot_path = folder / 'evidence' / 'after-execution.json'
        result['source_integrity'] = (workspace_snapshot(folder / 'workspace') == json.loads(snapshot_path.read_text(encoding='utf-8'))) if snapshot_path.exists() else None
        if result['source_integrity'] is False:
            result.update(passed=False, bridge_cycle_verified=False, evidence_class='BLOCKED',
                          blocker='Source changed after the recorded execution; re-verification required')
        if not result['suite_integrity']:
            result.update(passed=False, bridge_cycle_verified=False, evidence_class='BLOCKED', blocker='Acceptance suite no longer matches its recorded hash')
        if project['stage'] in ('BLOCKED', 'NEEDS_HUMAN'):
            result['evidence_class'] = 'BLOCKED'
        (folder / 'report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        md = (f"# Pello Phase 2\n\nProject: {project_id}\nTask: {project['task_id']}\n\n"
              f"State: {result['stage']} | Evidence: {result['evidence_class']}\n\n"
              f"Reserved SDK turns: {len(operations)}/3 | Model: {project['model']} ({project['effort']})\n\n"
              f"Supervisor decision: {decision['decision'] if decision else 'unavailable'}\n\n"
              f"Independent verification: {verification if verification else 'not executed'}\n\n"
              f"Blocker: {result['blocker'] or 'none'}\n\nFull exchanges and role sessions: report.json. "
              "No repair or next-task execution was started. Full V1 is not complete.\n")
        (folder / 'report.md').write_text(md, encoding='utf-8')
        return result
