import json
from pathlib import Path
import tempfile
import unittest
from athis_autopilot.supervised import SupervisedCycle
from phase2_support import make_project


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.cycle, self.project_id, self.backend = make_project(self.tmp.name)

    def test_plan_and_message_persist_across_restart(self):
        self.cycle._plan(self.cycle.project(self.project_id))
        reopened = SupervisedCycle(self.cycle.root, backend=self.backend)
        self.assertEqual(reopened.project(self.project_id)['stage'], 'PLANNED')
        self.assertEqual(len(reopened.tasks(self.project_id)), 1)
        self.assertEqual(reopened.exchanges(self.project_id)[0]['origin'], 'supervisor_ai')
        self.assertEqual(len(reopened.sessions(self.project_id)), 1)

    def test_duplicate_project_rejected(self):
        with self.assertRaises(ValueError):
            self.cycle.create_supervised(Path(self.tmp.name) / 'spec.md', Path(self.tmp.name) / 'owner-tests', project_id=self.project_id)

    def test_migration_preserves_original_tables_and_data(self):
        with self.cycle.db() as cx:
            cx.execute("INSERT INTO events(job_id,at,kind,details) VALUES('old','then','old','{}')")
        reopened = SupervisedCycle(self.cycle.root, backend=self.backend)
        with reopened.db() as cx:
            self.assertEqual(cx.execute("SELECT count(*) FROM events WHERE job_id='old'").fetchone()[0], 1)
            self.assertEqual(cx.execute('SELECT count(*) FROM pello_migrations WHERE version=2').fetchone()[0], 1)

    def test_in_flight_restart_blocks_without_new_call(self):
        project = self.cycle.project(self.project_id)
        self.cycle._session(project, 'supervisor')
        self.cycle.reserve(self.project_id, 'plan', {'role': 'supervisor'})
        result = SupervisedCycle(self.cycle.root, backend=self.backend).run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertIn('reconcile', result['blocker'])
        self.assertEqual(len(self.backend.calls), 0)

    def test_completed_sdk_output_recovers_without_repeating_turn(self):
        self.backend.crash_after_write = 'plan'
        with self.assertRaises(SystemExit): self.cycle.run_supervised(self.project_id)
        result = SupervisedCycle(self.cycle.root, backend=self.backend).run_supervised(self.project_id)
        self.assertTrue(result['passed'])
        self.assertEqual([x[0] for x in self.backend.calls], ['plan', 'execute', 'review'])

    def test_invalid_structured_response_is_saved_but_not_processed(self):
        self.backend.bad_phase = 'plan'
        result = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertEqual(self.cycle.tasks(self.project_id), [])
        self.assertEqual(self.cycle.operation(self.project_id, 'plan')['status'], 'COMPLETED')

    def test_three_operation_cap(self):
        for phase in ('plan', 'execute', 'review'): self.cycle.reserve(self.project_id, phase, {})
        with self.assertRaises(ValueError): self.cycle.reserve(self.project_id, 'extra', {})

    def test_wrong_executor_correlation_blocks(self):
        self.backend.wrong_phase = 'execute'
        result = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertIn('correlation', result['blocker'])
        self.assertEqual(len(self.backend.calls), 2)

    def test_wrong_supervisor_project_blocks(self):
        self.backend.wrong_phase = 'plan'
        result = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertEqual(result['tasks'], [])

    def test_failed_nested_turn_does_not_retry(self):
        self.backend.failure = 'execute'
        result = self.cycle.run_supervised(self.project_id)
        result_again = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertEqual(result_again['stage'], 'BLOCKED')
        self.assertFalse(result['passed'])
        self.assertEqual(len(self.backend.calls), 2)

    def test_suite_tamper_blocks_before_verification(self):
        self.cycle._plan(self.cycle.project(self.project_id))
        self.cycle._execute(self.cycle.project(self.project_id))
        path = self.cycle.folder(self.project_id) / 'acceptance/test_example.py'
        path.chmod(0o644); path.write_text('pass\n')
        result = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertFalse(result['suite_integrity'])
        self.assertEqual(len(self.backend.calls), 2)

    def test_fake_evidence_never_becomes_real_after_restart(self):
        self.cycle.run_supervised(self.project_id)
        result = SupervisedCycle(self.cycle.root).supervised_report(self.project_id)
        self.assertEqual(result['evidence_class'], 'MOCK VERIFIED')

    def test_duplicate_or_forward_task_dependencies_rejected(self):
        self.cycle._plan(self.cycle.project(self.project_id))
        decision = self.cycle.exchanges(self.project_id)[0]['payload']
        from athis_autopilot.messages import SupervisorDecision, parse_response
        from pydantic import ValidationError
        task = decision['tasks'][0]
        decision['tasks'] = [task, task]
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, json.dumps(decision))
        decision['tasks'] = [{**task, 'depends_on': ['future-task']}]
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, json.dumps(decision))

    def test_wrong_supervisor_review_task_rejected(self):
        self.backend.wrong_phase = 'review'
        result = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertEqual(len(self.backend.calls), 3)

    def test_shared_role_thread_rejected_before_executor_turn(self):
        original_prepare = self.backend.prepare
        def same_thread(**kwargs):
            ready = original_prepare(**kwargs)
            if kwargs['role'] == 'executor':
                ready['thread_id'] = self.cycle.sessions(self.project_id)[0]['thread_id']
                kwargs['thread_file'].write_text(ready['thread_id'])
            return ready
        self.backend.prepare = same_thread
        result = self.cycle.run_supervised(self.project_id)
        self.assertEqual(result['stage'], 'BLOCKED')
        self.assertEqual(len(self.backend.calls), 1)
