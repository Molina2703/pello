"""Budget-context regression through real Core/SQLite with a controlled engine."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from athis_autopilot.codex_worker import persist_session
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.product_planning import ProductPlanningCore,AnalysisReview
from tests.test_planning_graph import sample
from tests.test_planning_models import decision
from tests.test_product_planning import CAPABILITIES

class CapacityFollowingEngine:
    def __init__(self):self.payloads=[]
    def run(self,**kwargs):
        payload=json.loads((kwargs['out_dir']/'input.json').read_text())
        self.payloads.append(payload);capacity=payload['development_turns_remaining']
        decisions=[]
        for index,item in enumerate(payload['tasks']):
            d=decision();d.update(task_id=item['task_id'],expected_turns=1 if index==0 else max(1,capacity-1),evidence_refs=['task:'+item['task_id']])
            decisions.append(d)
        thread='controlled-capacity-planner';kwargs['thread_file'].write_text(thread)
        persist_session(SimpleNamespace(session_db=kwargs['session_db'],project_id=kwargs['project_id'],role=kwargs['role'],task_id=kwargs['task_id']),thread)
        return {'status':'completed','thread_id':thread,'turn_id':'controlled-capacity-turn','usage':{'total':1},'final_response':json.dumps({'decisions':decisions}),'error':None}

class ModelCapacityContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);base=Path(self.tmp.name)
        source=base/'source.md';source.write_text('# Product\n\nCollect cases.\n\nConnect vendor.\n\nExclude refunds.\n\nAuthorize messages.\n')
        self.backend=CapacityFollowingEngine();self.root=base/'runtime';self.pid='capacity'
        self.core=ProductPlanningCore(self.root,backend=self.backend,capabilities=CAPABILITIES);self.core.create_project(source,project_id=self.pid)
        a=sample().model_copy(update={'source_hash':hashlib.sha256(source.read_bytes()).hexdigest()})
        review=AnalysisReview(verdict='PASS',findings=[],coverage='adequate',contradictions='adequate',blocking_classification='adequate',source_traceability='adequate',exclusions_and_untrusted_text='preserved',rationale='Controlled budget integration fixture, not SDK evidence.')
        with self.core.db() as c:
            c.execute('insert into pello_product_analysis_history values(?,?,?,?,?,?,?,?)',(self.pid,1,1,a.model_dump_json(),review.model_dump_json(),'ANALYSIS_ACCEPTED','controlled fixture','2026-10-25T00:00:00+00:00'))
            c.execute("update pello_product_versions set analysis=?,analysis_review=?,status='ANALYSIS_ACCEPTED' where project_id=?",(a.model_dump_json(),review.model_dump_json(),self.pid))
            c.execute('create table pello_product_run_authorizations(id TEXT,grant_json TEXT,deadline TEXT,max_turns INTEGER)')
            c.execute("insert into pello_product_run_authorizations values('unit','{}','2099-01-01T00:00:00+00:00',6)")
        self.increments={'proposal':{'increments':[{'task_id':task,'objective':'Bounded local task','requirement_ids':[a.requirements[0].requirement_id],'operation_kind':'local_logic','boundary_rationale':'Small local capability','verification_evidence':['Proposed local checks']} for task in ['ONE','TWO']]}}
        self.models=self.core.folder(self.pid)/'evidence/version-1/planning/models.json'
    def propose(self,core=None):
        core=core or self.core
        with patch.object(core,'planning_stage',return_value=self.increments):return core.propose_models(self.pid)
    def test_new_request_advertises_exact_post_reservation_validation_capacity(self):
        result=self.propose();advertised=self.backend.payloads[0]['development_turns_remaining']
        self.assertEqual(advertised,5)
        self.assertTrue(all(r['budget_assessment']['remaining_development_turns']==advertised for r in result['records']))
        self.assertTrue(result['aggregate_budget_assessment']['combined_estimate_fits_development_capacity'])
        self.assertFalse(result['aggregate_budget_assessment']['product_execution_authorized'])
        with self.core.db() as c:self.assertEqual(c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0],1)
    def test_missing_stage_replay_keeps_same_capacity_and_no_duplicate_reservation(self):
        first=self.propose();self.models.unlink()
        restarted=ProductPlanningCore(self.root,backend=self.backend,capabilities=CAPABILITIES)
        again=self.propose(restarted)
        self.assertEqual(len(self.backend.payloads),1)
        self.assertEqual(first['proposal'],again['proposal'])
        self.assertTrue(again['aggregate_budget_assessment']['combined_estimate_fits_development_capacity'])
        self.assertEqual(again['aggregate_budget_assessment']['development_capacity_at_decision'],5)
        with self.core.db() as c:self.assertEqual(c.execute('select count(*) from pello_product_operations').fetchone()[0],1)
    def test_legacy_pre_reservation_context_replays_unchanged_and_retains_shortfall(self):
        self.propose();self.models.unlink()
        path=self.core.folder(self.pid)/'evidence/version-1/plan-models/input.json'
        payload=json.loads(path.read_text());payload.pop('development_capacity_scope',None);payload['development_turns_remaining']=6
        path.write_text(json.dumps(payload));before=path.read_bytes()
        with self.core.db() as c:
            row=c.execute('select request,response from pello_product_operations').fetchone();request=json.loads(row['request']);raw=json.loads(row['response'])
            request['input_sha256']=hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()
            answer=json.loads(raw['final_response']);answer['decisions'][1]['expected_turns']=5;raw['final_response']=json.dumps(answer)
            c.execute('update pello_product_operations set request=?,response=?',(json.dumps(request),json.dumps(raw)))
        result=self.propose();self.assertEqual(path.read_bytes(),before);self.assertEqual(len(self.backend.payloads),1)
        self.assertEqual(result['aggregate_budget_assessment']['development_capacity_at_decision'],5)
        self.assertEqual(result['aggregate_budget_assessment']['shortfall'],1)
        self.assertFalse(result['aggregate_budget_assessment']['product_execution_authorized'])
    def test_no_post_selection_capacity_blocks_before_reservation(self):
        with self.core.db() as c:c.execute('update pello_product_run_authorizations set max_turns=1')
        with self.assertRaises(CodexBlocked):self.propose()
        self.assertEqual(self.backend.payloads,[])
        with self.core.db() as c:self.assertEqual(c.execute('select count(*) from pello_product_operations').fetchone()[0],0)

if __name__=='__main__':unittest.main()
