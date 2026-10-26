"""Bounded Planner recovery preserves validation, source and ordinary success."""
import copy,json,tempfile,unittest
from pathlib import Path
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.planning_contracts import ArchitectureProposal
from tests.test_planning_graph import sample,proposal

class ArchitectureValidationRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.analysis=sample();self.good=proposal(self.analysis);self.bad=copy.deepcopy(self.good)
        ids=[r.requirement_id for r in self.analysis.requirements]
        # A legitimate source prerequisite exists but its owning task is absent
        # from INVOICE's ancestry. This is rejected by the existing validator.
        self.analysis.requirements[5].depends_on=[ids[0]]
        self.bad['nodes'][1]['depends_on']=[]
        self.core=object.__new__(ProductPlanningCore)
        self.source={'project_id':'unit','version':1,'source_sha256':'a'*64,'requirements':self.analysis.model_dump(mode='json'),'execution_authorized':False}
        self.core.planner_input=lambda _:copy.deepcopy(self.source)
        self.core.version_row=lambda _:{'version':1};self.core.folder=lambda _:Path(self.tmp.name)
        self.calls=[];self.model_calls=[];self.cache={};self.responses=[self.bad,self.good];self.block_recovery=False
        self.core._invoke=self.invoke

    def invoke(self,pid,version,phase,role,payload,schema):
        self.calls.append((phase,role,copy.deepcopy(payload)))
        if self.block_recovery and len(self.calls)>1:raise CodexBlocked('STOP or budget gate')
        if phase not in self.cache:
            self.cache[phase]=ArchitectureProposal.model_validate(self.responses[len(self.model_calls)])
            self.model_calls.append(phase)
        return self.cache[phase],{}

    def test_invalid_graph_gets_one_planner_correction_with_exact_source(self):
        result=self.core.propose_architecture('unit')
        self.assertEqual(len(self.model_calls),2);self.assertTrue(result['validation']['ready'])
        phase,role,payload=self.calls[1]
        self.assertEqual(role,'planner');self.assertNotEqual(phase,self.calls[0][0])
        for key,value in self.source.items():self.assertEqual(payload[key],value)
        feedback=payload['architecture_validation_feedback']
        self.assertEqual(feedback['rejected_proposal'],self.bad)
        self.assertIn('prerequisites',feedback['validation_error'])
        rejected=Path(self.tmp.name)/'evidence/version-1/planning/architecture-initial-rejection.json'
        self.assertEqual(json.loads(rejected.read_text())['proposal'],self.bad)
        self.assertFalse(result['validation']['execution_authorized'])

    def test_initial_valid_graph_keeps_original_single_call_and_result(self):
        self.responses=[self.good];result=self.core.propose_architecture('unit')
        self.assertEqual(self.model_calls,['plan-architecture']);self.assertEqual(result['proposal'],self.good)
        self.assertFalse((Path(self.tmp.name)/'evidence/version-1/planning/architecture-initial-rejection.json').exists())

    def test_second_invalid_graph_remains_failure_and_cannot_be_persisted_as_valid(self):
        self.responses=[self.bad,self.bad]
        with self.assertRaisesRegex(ValueError,'prerequisites'):self.core.propose_architecture('unit')
        self.assertEqual(len(self.model_calls),2)
        self.assertFalse((Path(self.tmp.name)/'evidence/version-1/planning/architecture.json').exists())

    def test_existing_guard_can_block_correction_without_accepting_original(self):
        self.block_recovery=True
        with self.assertRaises(CodexBlocked):self.core.propose_architecture('unit')
        self.assertEqual(len(self.model_calls),1)
        self.assertFalse((Path(self.tmp.name)/'evidence/version-1/planning/architecture.json').exists())

    def test_replay_uses_same_phases_and_saved_results_without_extra_model_call(self):
        result=self.core.propose_architecture('unit');again=self.core.propose_architecture('unit')
        self.assertEqual(result,again);self.assertEqual(len(self.model_calls),2)
