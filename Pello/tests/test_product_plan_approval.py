"""Approval/recovery gate tests with an explicitly mocked SDK backend."""
import unittest
from unittest.mock import patch
from athis_autopilot.engines import CodexBlocked
from tests import test_product_plan_recovery as fixtures


class ProductPlanApprovalTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.ProductPlanRecoveryTests();self.fixture.setUp();self.addCleanup(self.fixture.tearDown)
        self.core=self.fixture.core;self.pid=self.fixture.pid
        self.core.persist_plan(self.pid)
        digest=self.core.reconstruct_plan(self.pid)['plan_sha256']
        self.evidence={'objective':'Synthetic approval-gate unit fixture only','changed_files':[],
            'diff':'Synthetic unit test data','test_command':['mocked objective check'],'test_exit_code':0,
            'tests_run':1,'tests_passed':1,'tests_failed':0,
            'scope_constraints':[{'plan_sha256':digest,'regression':{'exit_code':0,'tests_run':1},'protected_suites_intact':True}]}
        self.core.create_project(self.fixture.source,project_id='independent-review')
    def review(self):
        self.core.review_engineering_increment('independent-review','3c2-b6-unit',evidence=self.evidence)
    def approve(self):return self.core.approve_plan(self.pid,review_project_id='independent-review',review_phase='engineering-review-3c2-b6-unit')
    def test_recorded_independent_pass_accepts_and_restart_preserves_checkpoint(self):
        self.review();result=self.approve();self.assertEqual(result['approval'],'ACCEPTED')
        self.assertTrue(self.core.status(self.pid)['plan_ready'])
        self.assertEqual(self.core.reconstruct_plan(self.pid)['plan_sha256'],result['plan_sha256'])
        with self.core.db() as cx:self.assertEqual(cx.execute("SELECT count(*) FROM pello_product_checkpoints WHERE phase='plan-accepted'").fetchone()[0],1)
    def test_failed_objective_gate_cannot_be_overridden_by_reviewer_pass(self):
        self.evidence['scope_constraints'][0]['regression']['exit_code']=1;self.review()
        with self.assertRaises(CodexBlocked):self.approve()
        self.assertFalse(self.core.status(self.pid)['plan_ready'])
    def test_interrupted_accepted_checkpoint_recovers_without_repeating_review(self):
        self.review();before=len(self.fixture.backend.calls)
        with patch.object(self.core,'_checkpoint',side_effect=RuntimeError('simulated checkpoint interruption')):
            with self.assertRaises(RuntimeError):self.approve()
        self.assertEqual(self.core.reconstruct_plan(self.pid)['approval'],'ACCEPTED')
        self.assertEqual(len(self.fixture.backend.calls),before)


if __name__=='__main__':unittest.main()
