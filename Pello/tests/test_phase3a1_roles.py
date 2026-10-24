"""Role/session/model tests use injected models; no live SDK calls."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from pipeline_support import PipelineBackend, fixture
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.model_policy import select_model
from athis_autopilot.pipeline import IncrementalPipeline
from athis_autopilot.pipeline_contracts import ModelProfile, PipelinePolicy


class RolePolicyTests(unittest.TestCase):
    def test_defaults_by_responsibility_and_deterministic_tester_option(self):
        policy = PipelinePolicy(); capabilities = PipelineBackend().capabilities()
        for phase, role, model, effort in [('plan', 'planner', 'gpt-6.1-sol', 'high'),
                ('A/attempt-1/execute', 'coder', 'gpt-6-luna', 'medium'),
                ('A/attempt-1/review', 'reviewer', 'gpt-6.1-sol', 'high'),
                ('test-design', 'tester', 'gpt-6.1-sol', 'medium')]:
            with self.subTest(role=role):
                result = select_model(policy, capabilities, phase=phase, responsibility=role)
                self.assertEqual((result['model'], result['effort'], result['responsibility']), (model, effort, role))

    def test_lighter_profiles_and_coder_escalation(self):
        policy = PipelinePolicy()
        policy.role_profiles['planner'] = ModelProfile(model='gpt-6-luna', effort='low')
        caps = PipelineBackend().capabilities()
        self.assertEqual(select_model(policy, caps, phase='plan')['model'], 'gpt-6-luna')
        self.assertEqual(select_model(policy, caps, phase='execute', attempt=2)['model'], 'gpt-6.1-sol')
        self.assertEqual(select_model(policy, caps, phase='execute', risk='high')['reason'], 'risk/failure escalation')
        self.assertEqual(select_model(policy, caps, phase='review', attempt=2)['effort'], 'high')
        configured = PipelinePolicy(advanced_effort='high')
        self.assertEqual(select_model(configured, caps, phase='plan')['effort'], 'high')
        self.assertEqual(select_model(configured, caps, phase='execute', attempt=2)['effort'], 'high')
        self.assertTrue(configured.role_profiles)

    def test_unavailable_model_effort_missing_profile_and_unknown_role_fail_closed(self):
        caps = PipelineBackend().capabilities(); caps['models']['gpt-6.1-sol'] = ['medium']
        with self.assertRaises(CodexBlocked): select_model(PipelinePolicy(), caps, phase='plan')
        policy = PipelinePolicy(); del policy.role_profiles['reviewer']
        with self.assertRaises(CodexBlocked): select_model(policy, caps, phase='review')
        with self.assertRaises(CodexBlocked): select_model(PipelinePolicy(), caps, phase='unknown')
        with self.assertRaises(ValueError): ModelProfile(model='gpt-6-astra', effort='high')

    def test_old_persisted_policy_keeps_original_models_and_efforts(self):
        raw = {'max_attempts': 1, 'max_turns': 5, 'review': 'every_increment',
               'routine_model': 'gpt-6-luna', 'advanced_model': 'gpt-6.1-sol',
               'routine_effort': 'low', 'advanced_effort': 'medium'}
        original = json.dumps(raw)
        policy = PipelinePolicy.model_validate_json(original)
        self.assertEqual(policy.role_profiles, {})
        for phase in ('plan', 'execute', 'review'):
            selected = select_model(policy, PipelineBackend().capabilities(), phase=phase)
            self.assertEqual((selected['model'], selected['effort']), ('gpt-6-luna', 'low'))
        self.assertEqual(json.dumps(raw), original)
        self.assertEqual(PipelinePolicy.model_validate_json(PipelinePolicy().model_dump_json()).role_profiles,
                         PipelinePolicy().role_profiles)


class IndependentReviewerTests(unittest.TestCase):
    def test_legacy_plan_output_replays_without_repeating_planning(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            with patch.object(core, 'exchange', side_effect=SystemExit('After durable plan response')):
                with self.assertRaises(SystemExit): core.run_pipeline(pid)
            # Inject the layout of a pre-v4 in-flight plan, retaining its thread
            # and response instead of pretending it was a new independent role.
            folder = core.folder(pid)
            (folder / 'planner-thread.txt').rename(folder / 'supervisor-thread.txt')
            with core.db() as cx:
                cx.execute("UPDATE pello_sessions SET role='supervisor' WHERE project_id=? AND role='planner'", (pid,))
                op = core.operation(pid, 'plan'); request = json.loads(op['request']); request['role'] = 'supervisor'
                cx.execute('UPDATE pello_pipeline_operations SET request=? WHERE project_id=? AND phase=?',
                           (json.dumps(request), pid, 'plan'))
            restored_backend = PipelineBackend()
            result = IncrementalPipeline(core.root, backend=restored_backend).run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertFalse(any(call[2] == 'plan' for call in restored_backend.calls))
            self.assertEqual({s['role'] for s in result['sessions']}, {'supervisor', 'executor', 'reviewer'})

    def test_legacy_review_is_not_relabelled_as_independent(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            core._ensure_capabilities(pid); core._plan_pipeline(core.project(pid))
            task = core.tasks(pid)[0]; attempt = core._next_attempt(core.project(pid), task)
            core._execute_increment(core.project(pid), task, attempt)
            attempt = core.attempts(pid)[-1]
            core._verify_increment(core.project(pid), task, attempt)
            core.reserve(pid, 'A/attempt-1/review', {'role': 'supervisor'})
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertEqual(result['checkpoints'], [])
            self.assertIn('independent reviewer context', result['blocker'])
            self.assertFalse(any(call[2] == 'review' for call in backend.calls))

    def test_distinct_persisted_threads_objective_context_and_resume(self):
        class Backend(PipelineBackend):
            def run(self, **kwargs):
                raw = super().run(**kwargs)
                payload = json.loads(raw['final_response'])
                if kwargs['out_dir'].name == 'plan': payload['reasoning_summary'] = 'PLANNER_PRIVATE_SENTINEL'
                if kwargs['out_dir'].name == 'execute': payload['execution_summary'] = 'CODER_PRIVATE_SENTINEL'
                raw['final_response'] = json.dumps(payload)
                (kwargs['out_dir'] / 'codex_result.json').write_text(json.dumps(raw))
                return raw
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, _ = fixture(tmp, backend=Backend())
            first = core.run_pipeline(pid, stop_after=1)
            sessions = first['sessions']
            self.assertEqual({s['role'] for s in sessions}, {'planner', 'executor', 'reviewer'})
            self.assertEqual(len({s['thread_id'] for s in sessions}), 3)
            restored = IncrementalPipeline(core.root, backend=Backend())
            result = restored.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertEqual({s['role']: s['thread_id'] for s in sessions},
                             {s['role']: s['thread_id'] for s in result['sessions']})
            for operation in result['operations']:
                request = json.loads(operation['request'])
                self.assertIn('responsibility', request['selection'])
                if operation['phase'].endswith('/review'):
                    self.assertEqual(request['role'], 'reviewer')
                    self.assertNotIn('PLANNER_PRIVATE_SENTINEL', request['prompt'])
                    self.assertNotIn('CODER_PRIVATE_SENTINEL', request['prompt'])
                    data = json.loads(request['prompt'].split('PIPELINE CONTEXT (JSON):\n')[1])
                    self.assertTrue(data['verification']['passed'])
                    self.assertIn('actual_source', data); self.assertIn('git_diff', data)
                    self.assertNotIn('global_plan', data); self.assertNotIn('plan', data['current_increment'])
            before = len(result['operations'])
            self.assertEqual(len(restored.run_pipeline(pid)['operations']), before)

    def test_duplicate_reviewer_identity_is_rejected(self):
        class Backend(PipelineBackend):
            def prepare(self, **kwargs):
                ready = super().prepare(**kwargs)
                if kwargs['role'] == 'reviewer':
                    ready['thread_id'] = kwargs['thread_file'].with_name('planner-thread.txt').read_text()
                    kwargs['thread_file'].write_text(ready['thread_id'])
                return ready
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, _ = fixture(tmp, backend=Backend())
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertEqual(result['checkpoints'], [])
            self.assertIn('UNIQUE', result['blocker'])


class SessionMigrationTests(unittest.TestCase):
    def old_database(self, root):
        root = Path(root)
        rows = [('old-project', 'supervisor', 'old-planner-thread', 'then', 'old-review-turn', 'T1', 'READY'),
                ('old-project', 'executor', 'old-coder-thread', 'then', 'old-code-turn', 'T1', 'READY')]
        with closing(sqlite3.connect(root / 'jobs.sqlite3')) as cx, cx:
            cx.executescript('''CREATE TABLE pello_migrations(version INTEGER PRIMARY KEY, applied TEXT NOT NULL);
                INSERT INTO pello_migrations VALUES(2,'then'); INSERT INTO pello_migrations VALUES(3,'then');
                CREATE TABLE pello_sessions(project_id TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('supervisor','executor')), thread_id TEXT NOT NULL UNIQUE,
                created TEXT NOT NULL, last_successful_turn TEXT, task_id TEXT, status TEXT NOT NULL,
                PRIMARY KEY(project_id,role));''')
            cx.executemany('INSERT INTO pello_sessions VALUES(?,?,?,?,?,?,?)', rows)
        return rows

    def test_migration_preserves_every_historical_session_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.old_database(tmp)
            core = IncrementalPipeline(Path(tmp), backend=PipelineBackend())
            self.assertEqual(core.sessions('old-project'), [dict(zip(
                ('project_id', 'role', 'thread_id', 'created', 'last_successful_turn', 'task_id', 'status'), row))
                for row in sorted(rows, key=lambda r:r[1])])
            IncrementalPipeline(Path(tmp), backend=PipelineBackend())
            with core.db() as cx:
                self.assertEqual(cx.execute('SELECT count(*) FROM pello_migrations WHERE version=4').fetchone()[0], 1)
                cx.execute('INSERT INTO pello_sessions VALUES(?,?,?,?,?,?,?)',
                    ('new-project', 'reviewer', 'new-independent-thread', 'now', None, None, 'READY'))
                self.assertEqual(cx.execute('PRAGMA integrity_check').fetchone()[0], 'ok')

    def test_failed_migration_rolls_back_session_schema_and_data(self):
        real_connect = sqlite3.connect
        class Interrupted(sqlite3.Connection):
            def execute(self, sql, *args):
                if sql == 'DROP TABLE pello_sessions_before_v4': raise sqlite3.OperationalError('Injected migration failure')
                return super().execute(sql, *args)
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.old_database(tmp)
            def connect(*args, **kwargs): return real_connect(*args, **kwargs, factory=Interrupted)
            with patch('athis_autopilot.supervisor.sqlite3.connect', connect), self.assertRaises(sqlite3.OperationalError):
                IncrementalPipeline(Path(tmp), backend=PipelineBackend())
            with closing(real_connect(Path(tmp) / 'jobs.sqlite3')) as cx:
                self.assertEqual(cx.execute('SELECT * FROM pello_sessions ORDER BY rowid').fetchall(), rows)
                self.assertIsNone(cx.execute('SELECT 1 FROM pello_migrations WHERE version=4').fetchone())
                self.assertIsNone(cx.execute("SELECT 1 FROM sqlite_master WHERE name='pello_sessions_before_v4'").fetchone())
