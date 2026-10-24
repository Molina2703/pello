import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pipeline_support import fixture, PipelineBackend
from phase2_support import make_project
from athis_autopilot.pipeline import IncrementalPipeline
from athis_autopilot.pipeline_contracts import PipelineManifest, PipelinePolicy
from athis_autopilot.model_policy import select_model
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.supervised import SupervisedCycle


class PipelineTests(unittest.TestCase):
    def test_two_dependent_increments_and_real_local_tests(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            result = core.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertEqual(result['evidence_class'], 'TESTED WITH MOCKS')
            self.assertEqual(backend.calls, [('_plan', 0, 'plan'), ('A', 1, 'execute'), ('A', 1, 'review'), ('B', 1, 'execute'), ('B', 1, 'review')])
            verification = [e['payload'] for e in result['exchanges'] if e['kind'] == 'verification']
            self.assertEqual([len(v['suites']) for v in verification], [1, 2])
            self.assertEqual([t['state'] for t in result['tasks']], ['APPROVED', 'APPROVED'])
            self.assertEqual(result['checkpoints'][1]['parent_head'], result['checkpoints'][0]['commit_sha'])
            self.assertIn('a.py', json.loads(result['checkpoints'][0]['snapshot']))
            self.assertIn('b.py', json.loads(result['checkpoints'][1]['snapshot']))
            self.assertEqual(len(result['sessions']), 2)

    def test_pause_restore_and_no_duplicate_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            first = core.run_pipeline(pid, stop_after=1)
            self.assertEqual(first['stage'], 'PAUSED'); self.assertEqual(first['verified_increments'], 1)
            restored_backend = PipelineBackend()
            restored = IncrementalPipeline(core.root, backend=restored_backend)
            result = restored.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertEqual(restored_backend.calls, [('B', 1, 'execute'), ('B', 1, 'review')])
            result = restored.run_pipeline(pid)
            self.assertTrue(result['passed']); self.assertEqual(len(restored_backend.calls), 2)
            self.assertEqual(len(result['checkpoints']), 2)

    def test_failure_blocks_dependents_and_records_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp, policy=PipelinePolicy(max_attempts=1))
            backend.always_bad = True
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertEqual(result['stage'], 'BLOCKED')
            self.assertEqual(result['verified_increments'], 0)
            self.assertFalse(any(c[0] == 'B' for c in backend.calls))
            self.assertFalse(any(c[2] == 'review' for c in backend.calls))
            self.assertEqual(result['attempts'][0]['stage'], 'FAILED')
            self.assertEqual(result['tasks'][1]['state'], 'PENDING')
            self.assertIn('test_value', result['attempts'][0]['feedback'])

    def test_bounded_repair_preserves_history_and_escalates(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            backend.fail_first = True
            result = core.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            history = [a for a in result['attempts'] if a['task_id'] == 'A']
            self.assertEqual([a['stage'] for a in history], ['FAILED', 'APPROVED'])
            self.assertEqual(len([e for e in result['exchanges'] if e['task_id'] == 'A' and e['kind'] == 'execution']), 2)
            repair_call = backend.calls.index(('A', 2, 'execute'))
            self.assertEqual(backend.choices[repair_call][0], 'gpt-6.1-sol')
            self.assertEqual(len(result['checkpoints']), 2)

    def test_read_only_reviewer_cannot_change_code(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            backend.mutate_review = True
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertEqual(result['verified_increments'], 0)
            self.assertIn('Read-only', result['blocker'])

    def test_review_failure_uses_repair_not_next_dependency(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            backend.reject_first_review = True
            result = core.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertLess(backend.calls.index(('A', 2, 'review')), backend.calls.index(('B', 1, 'execute')))

    def test_final_review_policy_omits_intermediate_ai_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp, policy=PipelinePolicy(review='final'))
            result = core.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertNotIn(('A', 1, 'review'), backend.calls)
            self.assertIn(('B', 1, 'review'), backend.calls)

    def test_incomplete_global_plan_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp); backend.bad_plan = True
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertIn('every owner increment', result['blocker'])
            self.assertEqual(len(backend.calls), 1)

    def test_model_budget_never_submits_an_extra_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp, policy=PipelinePolicy(max_turns=2))
            result = core.run_pipeline(pid)
            self.assertEqual(len(backend.calls), 2); self.assertEqual(result['stage'], 'BLOCKED')
            self.assertEqual(len(result['operations']), 2)
            core.run_pipeline(pid); self.assertEqual(len(backend.calls), 2)

    def test_result_replay_after_process_interruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp); backend.crash_after_output = True
            with self.assertRaises(SystemExit): core.run_pipeline(pid)
            restored_backend = PipelineBackend()
            restored = IncrementalPipeline(core.root, backend=restored_backend)
            result = restored.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertNotIn(('A', 1, 'execute'), restored_backend.calls)
            self.assertEqual(len(result['attempts']), 2)

    def test_unknown_inflight_operation_does_not_retry(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp); backend.block = True
            result = core.run_pipeline(pid)
            self.assertEqual(result['stage'], 'BLOCKED')
            core.run_pipeline(pid); self.assertEqual(len(backend.calls), 1)

    def test_checkpoint_commit_reconciles_after_crash(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            real_git = core._git
            def interrupted(workspace, *args):
                result = real_git(workspace, *args)
                if 'commit' in args: raise SystemExit('Crash after git commit')
                return result
            with patch.object(core, '_git', interrupted), self.assertRaises(SystemExit): core.run_pipeline(pid)
            result = core.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertEqual(backend.calls.count(('A', 1, 'execute')), 1)
            self.assertEqual(len(result['checkpoints']), 2)

    def test_checkpoint_source_or_head_drift_never_succeeds(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp); core.run_pipeline(pid)
            (core.folder(pid) / 'workspace/a.py').write_text('def value(): return 123\n')
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertFalse(result['integrity'])
            self.assertEqual(len(backend.calls), 5)

    def test_suite_tamper_blocks_before_inference(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            path = core.folder(pid) / 'acceptance/a/test_a.py'
            path.chmod(0o644); path.write_text('pass\n')
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertEqual(backend.calls, [])

    def test_existing_phase2_projects_survive_migration(self):
        with tempfile.TemporaryDirectory() as tmp:
            old, pid, backend = make_project(tmp)
            before = old.run_supervised(pid)
            IncrementalPipeline(old.root, backend=PipelineBackend())
            after = SupervisedCycle(old.root, backend=backend).run_supervised(pid)
            self.assertEqual(before['exchanges'], after['exchanges'])
            self.assertEqual(before['sessions'], after['sessions'])
            self.assertTrue(after['passed']); self.assertEqual(len(backend.calls), 3)

    def test_zero_test_suite_cannot_advance(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp, policy=PipelinePolicy(max_attempts=1))
            path = core.folder(pid) / 'acceptance/a/test_a.py'
            path.chmod(0o644); path.write_text('pass\n')
            from athis_autopilot.supervisor import files_hash
            with core.db() as cx:
                cx.execute('UPDATE pello_projects SET suite_hash=? WHERE id=?', (files_hash(path.parent.parent), pid))
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertEqual(result['verified_increments'], 0)
            self.assertFalse(any(c[0] == 'B' for c in backend.calls))

    def test_global_plan_and_verified_dependencies_reach_second_increment(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp); result = core.run_pipeline(pid)
            operation = next(o for o in result['operations'] if o['phase'] == 'B/attempt-1/execute')
            prompt = json.loads(operation['request'])['prompt']
            context = json.loads(prompt.split('PIPELINE CONTEXT (JSON):\n')[1])
            self.assertEqual(len(context['global_plan']['tasks']), 2)
            self.assertEqual(context['verified_dependencies'], [{'task_id': 'A', 'state': 'APPROVED'}])

    def test_completed_verifier_output_recovers_without_rerunning_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            real_exchange = core.exchange
            def crash(cx, project_id, task_id, attempt, kind, origin, payload):
                real_exchange(cx, project_id, task_id, attempt, kind, origin, payload)
                if kind == 'verification': raise SystemExit('Crash after verifier file before DB commit')
            with patch.object(core, 'exchange', crash), self.assertRaises(SystemExit): core.run_pipeline(pid)
            self.assertEqual(core.attempts(pid)[0]['stage'], 'VERIFYING')
            with patch.object(core, '_run_suite', wraps=core._run_suite) as runner:
                result = core.run_pipeline(pid)
            self.assertTrue(result['passed'], result['blocker'])
            self.assertEqual(runner.call_count, 2)  # Only B's new verification: regress A and test B.
            self.assertEqual(backend.calls.count(('A', 1, 'execute')), 1)

    def test_interrupted_verifier_without_result_requires_reconciliation(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            with patch.object(core, '_run_suite', side_effect=SystemExit('Verifier interrupted')), self.assertRaises(SystemExit):
                core.run_pipeline(pid)
            self.assertEqual(core.attempts(pid)[0]['stage'], 'VERIFYING')
            with patch.object(core, '_run_suite', wraps=core._run_suite) as runner:
                result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertIn('Interrupted verifier', result['blocker'])
            self.assertEqual(runner.call_count, 0)
            self.assertEqual(len(backend.calls), 2)

    def test_project_lock_prevents_a_second_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp)
            with core.project_lock(pid), self.assertRaises(CodexBlocked): core.run_pipeline(pid)
            self.assertEqual(backend.calls, [])

    def test_no_progress_stops_before_configured_attempt_ceiling(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp, policy=PipelinePolicy(max_attempts=4))
            backend.always_bad = True; result = core.run_pipeline(pid)
            self.assertEqual(len(result['attempts']), 2)
            self.assertIn('without observed source progress', result['blocker'])
            self.assertFalse(any(c[0] == 'B' for c in backend.calls))

    def test_head_drift_is_rejected_even_when_source_is_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp); core.run_pipeline(pid)
            workspace = core.folder(pid) / 'workspace'
            core._git(workspace, '-c', 'user.name=Test', '-c', 'user.email=test@localhost', 'commit', '--allow-empty', '-qm', 'unexpected')
            result = core.run_pipeline(pid)
            self.assertFalse(result['passed']); self.assertIn('head drift', result['blocker'])
            self.assertEqual(len(backend.calls), 5)


class PipelineContractsTests(unittest.TestCase):
    def test_manifest_dependency_cycle_and_path_escape_rejected(self):
        raw = json.loads((Path(__file__).resolve().parents[1] / 'examples/quotes/increments.json').read_text(encoding='utf-8'))
        for change in ('cycle', 'path'):
            value = json.loads(json.dumps(raw))
            if change == 'cycle': value['increments'][0]['depends_on'] = ['T2']
            else: value['increments'][0]['suite'] = '../outside'
            with self.assertRaises(ValueError): PipelineManifest.model_validate(value)

    def test_astra_and_external_execution_are_disallowed(self):
        with self.assertRaises(ValueError): PipelinePolicy(advanced_model='gpt-6-astra')
        raw = json.loads((Path(__file__).resolve().parents[1] / 'examples/quotes/increments.json').read_text(encoding='utf-8'))
        raw['tools'][0]['tool'] = 'n8n'; raw['tools'][0]['environment'] = 'development'
        with self.assertRaises(ValueError): PipelineManifest.model_validate(raw)

    def test_catalogue_validation_and_quota_fail_closed(self):
        policy = PipelinePolicy(); capabilities = PipelineBackend().capabilities()
        self.assertEqual(select_model(policy, capabilities, phase='execute')['model'], 'gpt-6-luna')
        self.assertEqual(select_model(policy, capabilities, phase='execute', attempt=2)['model'], 'gpt-6.1-sol')
        capabilities['remaining_percent'] = 0
        with self.assertRaises(CodexBlocked): select_model(policy, capabilities, phase='execute')
        capabilities['remaining_percent'] = None; capabilities['models'] = {}
        with self.assertRaises(CodexBlocked): select_model(policy, capabilities, phase='execute')
