"""Local integration tests: fake models, actual SQLite/files/subprocess verifier."""
from pathlib import Path
import tempfile
import unittest
from athis_autopilot.supervised import SupervisedCycle
from phase2_support import make_project


class LocalIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.cycle, self.project_id, self.backend = make_project(self.tmp.name)

    def test_end_to_end_bridge_and_actual_independent_verifier(self):
        result = self.cycle.run_supervised(self.project_id)
        self.assertTrue(result['passed'])
        self.assertEqual(result['verification']['tests_executed'], 1)
        self.assertEqual(result['tasks'][0]['state'], 'VERIFIED')
        self.assertEqual(result['execution']['files_modified'], ['example.py'])
        self.assertEqual(result['execution']['claimed_files_modified'], ['untrusted-claim.py'])
        self.assertEqual(len(result['exchanges']), 4)
        self.assertEqual(len({s['thread_id'] for s in result['sessions']}), 2)
        self.assertTrue(all(s['last_successful_turn'] for s in result['sessions']))
        review_prompt = self.backend.calls[-1][1]['prompt']
        self.assertIn('"verification_status": "PASSED"', review_prompt)
        self.assertIn('"files_modified": ["example.py"]', review_prompt)
        self.assertEqual(result['evidence_class'], 'MOCK VERIFIED')

    def test_restart_between_phases_and_completed_task_is_not_repeated(self):
        self.cycle._plan(self.cycle.project(self.project_id))
        restarted = SupervisedCycle(self.cycle.root, backend=self.backend)
        result = restarted.run_supervised(self.project_id)
        self.assertTrue(result['passed'])
        restarted.run_supervised(self.project_id)
        self.assertEqual([x[0] for x in self.backend.calls], ['plan', 'execute', 'review'])

    def test_failed_tests_cannot_be_overridden_by_complete(self):
        self.backend.bad_code = True
        result = self.cycle.run_supervised(self.project_id)
        self.assertFalse(result['passed'])
        self.assertEqual(result['stage'], 'NEEDS_HUMAN')
        self.assertEqual(result['tasks'][0]['state'], 'FAILED')
        self.assertEqual(result['supervisor_decision']['decision'], 'COMPLETE')
        self.assertEqual(result['verification']['failed'], 1)
        self.assertIn('rejected false COMPLETE', result['blocker'])

    def test_repair_is_persisted_and_stops_without_repair_turn(self):
        self.backend.bad_code = True; self.backend.review_action = 'REPAIR'
        result = self.cycle.run_supervised(self.project_id)
        self.assertTrue(result['cycle_finished'])
        self.assertFalse(result['passed'])
        self.assertEqual(result['supervisor_decision']['decision'], 'REPAIR')
        self.assertEqual(len(self.backend.calls), 3)

    def test_zero_executed_tests_never_passes(self):
        # Preserve declared expected count; replace this test's copied owner suite before creating another project.
        self.tmp2 = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp2.cleanup)
        cycle, project_id, _ = make_project(self.tmp2.name, empty_suite=True)
        result = cycle.run_supervised(project_id)
        self.assertFalse(result['passed'])
        self.assertEqual(result['verification']['tests_executed'], 0)

    def test_report_detects_changed_source_after_verification(self):
        result = self.cycle.run_supervised(self.project_id)
        self.assertTrue(result['passed'])
        (self.cycle.folder(self.project_id) / 'workspace/example.py').write_text('def value(): return 99\n')
        result = self.cycle.supervised_report(self.project_id)
        self.assertFalse(result['passed'])
        self.assertFalse(result['source_integrity'])
        self.assertEqual(result['evidence_class'], 'BLOCKED')

    def test_original_report_does_not_claim_failed_attempt_was_execution(self):
        from athis_autopilot.supervisor import Supervisor
        supervisor = Supervisor(Path(self.tmp.name) / 'old-runtime')
        base = Path(__file__).resolve().parents[1]
        job_id = supervisor.create(base / 'examples/clinica/spec.json', base / 'examples/clinica/acceptance', 'codex')
        supervisor.update(job_id, turns=1, state='BLOQUEADO')
        supervisor.report(job_id)
        import json
        report = json.loads((supervisor.root / 'jobs' / job_id / 'report.json').read_text())
        self.assertFalse(report['codex_executed'])
