import copy
import unittest
from athis_autopilot.planning_contracts import ArchitectureProposal, FunctionalIncrements, validate_increments
from tests.test_planning_graph import sample,proposal


def decomposition(a,p):
    return {'increments':[{**n,'inputs':['Recorded case data'],'outputs':['Inspectable functional result'],
        'interfaces':['Local function or isolated adapter'],'components':['product/'+n['task_id'].lower()+'.py'],
        'tools':['python','git'],'permissions':['Local development only'] if n['operation_kind']=='local_logic' else ['Separate vendor authorization required'],
        'external_effects':[] if n['operation_kind']=='local_logic' else ['Read/write vendor system'],
        'completion_conditions':['Observable result meets the source requirement'],
        'verification_evidence':['Deterministic acceptance results and independent review'],
        'boundary_rationale':'One user-observable capability with its own verification boundary.'} for n in p['nodes']]}


class FunctionalIncrementTests(unittest.TestCase):
    def setUp(self):
        self.a=sample();self.p=ArchitectureProposal.model_validate(proposal(self.a));self.d=decomposition(self.a,proposal(self.a))
    def check(self,**kwargs):return validate_increments(FunctionalIncrements.model_validate(self.d),self.p,self.a,**kwargs)
    def test_coverage_references_and_next_action(self):
        r=self.check();self.assertEqual(r['first_actionable'],'INTAKE');self.assertEqual(r['states']['INTAKE'],'ready')
        self.assertEqual(r['states']['INVOICE'],'dependency_blocked');self.assertEqual(r['states']['VENDOR'],'specification_blocked')
    def test_missing_increment(self):
        self.d['increments'].pop()
        with self.assertRaises(ValueError):self.check()
    def test_dependencies_cannot_be_silently_changed(self):
        self.d['increments'][1]['depends_on']=[]
        with self.assertRaises(ValueError):self.check()
    def test_requirement_mapping_cannot_drift(self):
        self.d['increments'][0]['requirement_ids']=self.d['increments'][1]['requirement_ids']
        with self.assertRaises(ValueError):self.check()
    def test_external_operation_requires_explicit_effects_and_permissions(self):
        for field in ('external_effects','permissions'):
            d=copy.deepcopy(self.d);d['increments'][-1][field]=[]
            with self.assertRaises(ValueError):validate_increments(FunctionalIncrements.model_validate(d),self.p,self.a)
    def test_local_logic_cannot_claim_external_effects(self):
        self.d['increments'][0]['external_effects']=['Send a message']
        with self.assertRaises(ValueError):self.check()
    def test_completed_prerequisite_unlocks_only_independent_work(self):
        r=self.check(completed={'INTAKE'})
        self.assertEqual(r['states']['INTAKE'],'completed');self.assertEqual(r['first_actionable'],'INVOICE')
        self.assertNotIn('VENDOR',r['ready'])
    def test_unsafe_component_path_rejected(self):
        self.d['increments'][0]['components']=['../outside.py']
        with self.assertRaises(ValueError):self.check()


if __name__=='__main__':unittest.main()
