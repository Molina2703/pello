"""Correction path through real Core invocation and SQLite, with a fake engine."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from athis_autopilot.codex_worker import persist_session
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.product_planning import ProductPlanningCore,AnalysisReview
from tests.test_planning_graph import sample,proposal
from tests.test_product_planning import CAPABILITIES

class ControlledArchitectureEngine:
    def __init__(self,analysis,root):self.analysis=analysis;self.root=root;self.calls=[];self.stop_after_first=False
    def run(self,**kwargs):
        phase=kwargs['out_dir'].name;self.calls.append(phase)
        thread='controlled-'+kwargs['role'];kwargs['thread_file'].write_text(thread)
        persist_session(SimpleNamespace(session_db=kwargs['session_db'],project_id=kwargs['project_id'],role=kwargs['role'],task_id=kwargs['task_id']),thread)
        value=proposal(self.analysis)
        if phase=='plan-architecture':value['nodes'][1]['depends_on']=[]
        if self.stop_after_first and len(self.calls)==1:(self.root/'STOP').write_text('stop before correction')
        return {'status':'completed','thread_id':thread,'turn_id':'controlled-'+phase,'usage':{'total':1},'final_response':json.dumps(value),'error':None}

class ArchitectureRecoveryLedgerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);base=Path(self.tmp.name)
        source=base/'source.md';source.write_text('# Product\n\nCollect cases.\n\nConnect vendor.\n\nExclude refunds.\n\nAuthorize messages.\n')
        self.analysis=sample().model_copy(update={'source_hash':hashlib.sha256(source.read_bytes()).hexdigest()})
        self.analysis.requirements[5].depends_on=[self.analysis.requirements[0].requirement_id]
        self.root=base/'runtime';self.backend=ControlledArchitectureEngine(self.analysis,self.root)
        self.core=ProductPlanningCore(self.root,backend=self.backend,capabilities=CAPABILITIES);self.pid='ledger';self.core.create_project(source,project_id=self.pid)
        review=AnalysisReview(verdict='PASS',findings=[],coverage='adequate',contradictions='adequate',blocking_classification='adequate',source_traceability='adequate',exclusions_and_untrusted_text='preserved',rationale='Synthetic integration fixture; no real SDK claim')
        with self.core.db() as c:
            c.execute('insert into pello_product_analysis_history values(?,?,?,?,?,?,?,?)',(self.pid,1,1,self.analysis.model_dump_json(),review.model_dump_json(),'ANALYSIS_ACCEPTED','controlled integration fixture','2026-10-25T00:00:00+00:00'))
            c.execute("update pello_product_versions set analysis=?,analysis_review=?,status='ANALYSIS_ACCEPTED' where project_id=?",(self.analysis.model_dump_json(),review.model_dump_json(),self.pid))
            c.execute('create table pello_product_run_authorizations(id TEXT,grant_json TEXT,deadline TEXT,max_turns INTEGER)')
            c.execute("insert into pello_product_run_authorizations values('unit','{}','2099-01-01T00:00:00+00:00',2)")
        self.directory=self.core.folder(self.pid)/'evidence/version-1/planning'

    def test_real_invoke_records_two_phases_and_restart_replays_durable_cache(self):
        result=self.core.propose_architecture(self.pid)
        self.assertEqual(self.backend.calls,['plan-architecture','plan-architecture-correction-1'])
        with self.core.db() as c:
            rows=[dict(r) for r in c.execute('select phase,status,request,response from pello_product_operations order by rowid')]
            self.assertEqual(len(rows),2);self.assertTrue(all(r['status']=='COMPLETED' for r in rows))
            self.assertEqual(c.execute('select used_turns from pello_product_projects').fetchone()[0],2)
            self.assertEqual(c.execute('select thread_id from pello_sessions').fetchone()[0],'controlled-planner')
        before=(self.directory/'architecture-initial-rejection.json').read_bytes()
        restarted=ProductPlanningCore(self.root,backend=self.backend,capabilities=CAPABILITIES)
        self.assertEqual(restarted.propose_architecture(self.pid),result)
        self.assertEqual(len(self.backend.calls),2);self.assertEqual((self.directory/'architecture-initial-rejection.json').read_bytes(),before)
        with restarted.db() as c:self.assertEqual(c.execute('select count(*) from pello_product_operations').fetchone()[0],2)

    def test_actual_cumulative_guard_rejects_second_reservation(self):
        with self.core.db() as c:c.execute('update pello_product_run_authorizations set max_turns=1')
        with self.assertRaises(CodexBlocked):self.core.propose_architecture(self.pid)
        self.assertEqual(len(self.backend.calls),1)
        with self.core.db() as c:
            self.assertEqual(c.execute('select count(*) from pello_product_operations').fetchone()[0],1)
            self.assertEqual(c.execute('select used_turns from pello_product_projects').fetchone()[0],1)
        self.assertFalse((self.directory/'architecture.json').exists())

    def test_actual_stop_guard_rejects_second_reservation(self):
        self.backend.stop_after_first=True
        with self.assertRaises(CodexBlocked):self.core.propose_architecture(self.pid)
        self.assertEqual(len(self.backend.calls),1)
        with self.core.db() as c:self.assertEqual(c.execute('select count(*) from pello_product_operations').fetchone()[0],1)
        self.assertFalse((self.directory/'architecture.json').exists())
