import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from athis_autopilot.product_planning import ProductPlanningCore,AnalysisReview
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.planning_contracts import ModelDecisionProposal,validate_model_decision,model_budget_summary
from athis_autopilot.pipeline import IncrementalPipeline
from athis_autopilot.model_policy import select_increment_model
from athis_autopilot.pipeline_contracts import PipelinePolicy
from tests.test_product_planning import FakeBackend,CAPABILITIES
from tests.test_planning_graph import sample,proposal
from tests.test_planning_increments import decomposition
from tests.test_planning_acceptance import contracts
from tests.test_planning_models import decision


class ProductPlanRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.base=Path(self.tmp.name)
        self.source=self.base/'source.md'
        self.source.write_text('# Product\n\nCollect cases.\n\nConnect vendor.\n\nExclude refunds.\n\nAuthorize messages.\n',encoding='utf-8')
        self.backend=FakeBackend();self.core=ProductPlanningCore(self.base/'runtime',backend=self.backend,capabilities=CAPABILITIES)
        self.pid='planning';self.core.create_project(self.source,project_id=self.pid)
        a=sample().model_copy(update={'source_hash':hashlib.sha256(self.source.read_bytes()).hexdigest()})
        review=AnalysisReview(verdict='PASS',findings=[],coverage='adequate',contradictions='adequate',blocking_classification='adequate',source_traceability='adequate',exclusions_and_untrusted_text='preserved',rationale='Synthetic unit fixture only')
        with self.core.db() as cx:
            cx.execute('INSERT INTO pello_product_analysis_history VALUES(?,?,?,?,?,?,?,?)',(self.pid,1,1,a.model_dump_json(),review.model_dump_json(),'ANALYSIS_ACCEPTED','mocked unit fixture','2026-10-25T00:00:00+00:00'))
            cx.execute("UPDATE pello_product_versions SET analysis=?,analysis_review=?,status='ANALYSIS_ACCEPTED' WHERE project_id=?",(a.model_dump_json(),review.model_dump_json(),self.pid))
        p=proposal(a);d=decomposition(a,p);c=contracts(a,p,d);records=[];decisions=[]
        for inc in d['increments']:
            md={**decision(),'task_id':inc['task_id']};decisions.append(md)
            records.append(validate_model_decision(ModelDecisionProposal.model_validate(md),CAPABILITIES,budget_remaining=12))
        models={'proposal':{'decisions':decisions},'records':records,'aggregate_budget_assessment':model_budget_summary(records)}
        self.directory=self.core.folder(self.pid)/'evidence/version-1/planning';self.directory.mkdir(parents=True)
        for name,value in [('architecture',{'proposal':p}),('increments',{'proposal':d}),('contracts',{'proposal':c}),('models',models)]:
            (self.directory/(name+'.json')).write_text(json.dumps(value),encoding='utf-8')
    def tearDown(self):self.tmp.cleanup()
    def test_persistence_restart_and_source_traceability(self):
        plan=self.core.persist_plan(self.pid)
        restarted=ProductPlanningCore(self.core.root,backend=FakeBackend(),capabilities=CAPABILITIES)
        self.assertEqual(restarted.reconstruct_plan(self.pid)['plan'],plan)
        self.assertEqual(plan['source_sha256'],hashlib.sha256(self.source.read_bytes()).hexdigest())
        self.assertFalse(self.backend.calls)
    def test_idempotence_does_not_duplicate_work_decisions_or_completions(self):
        first=self.core.persist_plan(self.pid);self.assertEqual(first,self.core.persist_plan(self.pid))
        with self.core.db() as cx:
            self.assertEqual(cx.execute('SELECT count(*) FROM pello_product_plan_history').fetchone()[0],1)
            self.assertEqual(cx.execute('SELECT count(*) FROM pello_product_model_decisions').fetchone()[0],3)
        self.assertEqual(self.core.inspect_plan(self.pid)['completed'],[])
    def test_changed_source_blocks_reuse_and_revalidation_preserves_old_plan(self):
        self.core.persist_plan(self.pid);self.source.write_text(self.source.read_text()+'\nNew scope.\n')
        with self.assertRaises(CodexBlocked):self.core.reconstruct_plan(self.pid)
        self.assertEqual(self.core.revalidate(self.pid),2)
        self.assertIsNone(self.core.version_row(self.pid)['plan'])
        self.assertIsNotNone(self.core.version_row(self.pid,1)['plan'])
    def test_missing_artifacts_reconstruct_without_inference(self):
        plan=self.core.persist_plan(self.pid);(self.directory/'execution-manifest.json').unlink()
        self.assertEqual(self.core.reconstruct_plan(self.pid)['plan'],plan)
        self.assertTrue((self.directory/'execution-manifest.json').is_file());self.assertFalse(self.backend.calls)
    def test_tampered_artifact_fails_closed(self):
        self.core.persist_plan(self.pid);(self.directory/'execution-manifest.json').write_text('{}')
        with self.assertRaises(CodexBlocked):self.core.reconstruct_plan(self.pid)
    def test_pipeline_consumes_generated_manifest_without_running_coder(self):
        plan=self.core.persist_plan(self.pid);r=IncrementalPipeline.inspect_planned_manifest(plan['manifest'])
        self.assertEqual(r['first_actionable'],'INTAKE');self.assertFalse(r['execution_authorized'])
        self.assertFalse(self.backend.calls)
    def test_blocked_branch_does_not_stop_unrelated_work(self):
        plan=self.core.persist_plan(self.pid);r=IncrementalPipeline.inspect_planned_manifest(plan['manifest'],completed={'INTAKE'})
        self.assertIn('INVOICE',r['ready']);self.assertNotIn('VENDOR',r['ready'])
    def test_task_profile_survives_high_risk_and_arbitrary_retry_number(self):
        owner={'coder_profile':{'model':'gpt-6-luna','effort':'high'},'risk':'high'}
        for attempt in (1,2,9):
            r=select_increment_model(PipelinePolicy(),CAPABILITIES,owner,phase='TASK/execute',attempt=attempt)
            self.assertEqual((r['model'],r['effort']),('gpt-6-luna','high'))
    def test_stop_prevents_persisting_new_plan(self):
        (self.core.root/'STOP').write_text('stop')
        with self.assertRaises(CodexBlocked):self.core.persist_plan(self.pid)
    def test_cumulative_budget_and_deadline_fail_closed(self):
        with self.core.db() as cx:
            cx.execute('CREATE TABLE pello_product_run_authorizations(id TEXT,grant_json TEXT,deadline TEXT,max_turns INTEGER)')
            cx.execute("INSERT INTO pello_product_run_authorizations VALUES('unit','{}','2099-01-01T00:00:00+00:00',0)")
        with self.assertRaises(CodexBlocked):self.core._budget_check(self.core.project_row(self.pid))
        with self.core.db() as cx:cx.execute("UPDATE pello_product_run_authorizations SET max_turns=30,deadline='2000-01-01T00:00:00+00:00'")
        with self.assertRaises(CodexBlocked):self.core._budget_check(self.core.project_row(self.pid))
    def test_no_approval_from_an_unrecorded_or_narrative_review(self):
        self.core.persist_plan(self.pid)
        with self.assertRaises(CodexBlocked):self.core.approve_plan(self.pid,review_project_id=self.pid,review_phase='engineering-review-missing')
        self.assertFalse(self.core.status(self.pid)['plan_ready'])
    def test_duplicate_model_decisions_rejected(self):
        p=self.directory/'models.json';m=json.loads(p.read_text());m['records'].append(m['records'][0]);p.write_text(json.dumps(m))
        with self.assertRaises(ValueError):self.core.persist_plan(self.pid)


if __name__=='__main__':unittest.main()
