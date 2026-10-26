"""Bounded contract batches preserve complete source and existing validation."""
import copy,json,tempfile,unittest
from pathlib import Path
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.planning_contracts import IncrementContracts
from tests.test_planning_graph import sample,proposal
from tests.test_planning_increments import decomposition
from tests.test_planning_acceptance import contracts

class ContractContextBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.a=sample();self.p=proposal(self.a);self.d=decomposition(self.a,self.p);self.c=contracts(self.a,self.p,self.d)
        self.padding='';self.calls=[];self.saved={};self.fail_once=False;self.bad=False
        self.core=object.__new__(ProductPlanningCore)
        self.core.planner_input=lambda _: {'requirements':self.a.model_dump(mode='json'),'execution_authorized':False,'context_padding':self.padding}
        self.core.planning_stage=lambda _,name: {'proposal':self.p if name=='architecture' else self.d}
        self.core.version_row=lambda _: {'version':1};self.core.folder=lambda _: Path(self.tmp.name)
        self.core._invoke=self.invoke
    def invoke(self,pid,version,phase,role,payload,model):
        if phase in self.saved:return self.saved[phase],{}
        self.assertLessEqual(len(self.core._prompt(phase,payload)),55000)
        if self.fail_once and self.calls:
            self.fail_once=False;raise RuntimeError('simulated interruption')
        self.calls.append((phase,copy.deepcopy(payload)))
        ids={i['task_id'] for i in payload['increments']['increments']}
        selected=[copy.deepcopy(c) for c in self.c['contracts'] if c['task_id'] in ids]
        if self.bad:selected=[]
        result=IncrementContracts.model_validate({'contracts':selected})
        self.saved[phase]=result;return result,{}
    def dense(self):
        original={}
        class Capture(Exception):pass
        def capture(*args,**kwargs):original.update(args[4]);raise Capture()
        self.core._invoke=capture
        with self.assertRaises(Capture):self.core.propose_contracts('unit')
        self.core._invoke=self.invoke
        for n in range(40000,55000,250):
            p=copy.deepcopy(original);p['context_padding']='x'*n
            single=copy.deepcopy(p);single['increments']['increments']=single['increments']['increments'][:1]
            try:self.core._prompt('plan-contracts',p)
            except ValueError:
                try:self.core._prompt('plan-contracts',single)
                except ValueError:continue
                self.padding='x'*n;return
        self.fail('Synthetic dense boundary not found')
    def test_dense_context_is_batched_with_complete_source_and_exact_increment_fields(self):
        self.dense();result=self.core.propose_contracts('unit');self.assertGreater(len(self.calls),1)
        seen=[]
        for _,p in self.calls:
            self.assertEqual(p['requirements'],self.a.model_dump(mode='json'))
            self.assertEqual(p['global_requirement_ids'],self.p['global_requirement_ids'])
            seen+=p['increments']['increments']
        self.assertEqual(seen,self.d['increments']);self.assertEqual(result['validation']['contract_count'],3)
        self.assertFalse(result['validation']['tests_executed'])
    def test_small_legacy_input_keeps_one_original_phase(self):
        self.core.propose_contracts('unit');self.assertEqual([p for p,_ in self.calls],['plan-contracts'])
    def test_interrupted_batches_replay_completed_response_without_duplicate_call(self):
        self.dense();self.fail_once=True
        with self.assertRaises(RuntimeError):self.core.propose_contracts('unit')
        result=self.core.propose_contracts('unit')
        self.assertEqual(len(self.calls),len({p for p,_ in self.calls}));self.assertEqual(len(result['proposal']['contracts']),3)
    def test_missing_batch_contract_cannot_produce_a_manifest(self):
        self.dense();self.bad=True
        with self.assertRaises(ValueError):self.core.propose_contracts('unit')
        self.assertFalse((Path(self.tmp.name)/'evidence/version-1/planning/contracts.json').exists())
    def test_irreducible_single_increment_rejected_before_any_model_call(self):
        self.padding='x'*60000
        with self.assertRaisesRegex(ValueError,'55,000'):self.core.propose_contracts('unit')
        self.assertEqual(self.calls,[])
