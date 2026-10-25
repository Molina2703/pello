import copy
import unittest
from athis_autopilot.planning_contracts import ArchitectureProposal,FunctionalIncrements,IncrementContracts,validate_contracts,manifest_from_contracts
from athis_autopilot.pipeline_contracts import PipelineManifest
from tests.test_planning_graph import sample,proposal
from tests.test_planning_increments import decomposition


def contracts(a,p,d):
    result=[]
    for inc in d['increments']:
        criteria=[]
        for kind in ('normal','invalid','boundary','permission'):
            criteria.append({'criterion_id':inc['task_id']+'-'+kind,'requirement_ids':inc['requirement_ids']+p['global_requirement_ids'],
                'kind':kind,'given':'A synthetic case and explicitly declared prerequisites','action':'Invoke the contracted behavior',
                'expected':'Return the documented result or reject invalid input without an external effect',
                'verification':'deterministic_local','state':'proposed'})
        result.append({'task_id':inc['task_id'],'preconditions':['A recorded synthetic case'],
            'data_structures':['Case record with stable identifier'],'business_rules':['Preserve original requirements and exclusions'],
            'validation_behavior':['Reject malformed input'],'error_behavior':['Return an inspectable failure without side effects'],
            'criteria':criteria,'unresolved_issue_ids':[]})
    return {'contracts':result}


class PlanningAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.a=sample();self.p=proposal(self.a);self.d=decomposition(self.a,self.p);self.c=contracts(self.a,self.p,self.d)
    def validate(self):return validate_contracts(IncrementContracts.model_validate(self.c),FunctionalIncrements.model_validate(self.d),ArchitectureProposal.model_validate(self.p),self.a)
    def test_contracts_are_proposals_not_executed_tests(self):
        result=self.validate();self.assertEqual(result['test_lifecycle'],'not_generated')
        self.assertFalse(result['tests_executed']);self.assertFalse(result['tests_protected'])
    def test_existing_manifest_accepts_automatic_conversion(self):
        m=manifest_from_contracts(IncrementContracts.model_validate(self.c),FunctionalIncrements.model_validate(self.d),ArchitectureProposal.model_validate(self.p),self.a)
        self.assertIsInstance(PipelineManifest.model_validate(m.model_dump()),PipelineManifest)
        self.assertEqual(m.increments[0].task_id,'INTAKE');self.assertTrue(m.increments[0].acceptance_criteria)
    def test_missing_contract_rejected(self):
        self.c['contracts'].pop()
        with self.assertRaises(ValueError):self.validate()
    def test_normal_invalid_and_boundary_coverage_required(self):
        for kind in ('normal','invalid','boundary'):
            d=copy.deepcopy(self.c);d['contracts'][0]['criteria']=[c for c in d['contracts'][0]['criteria'] if c['kind']!=kind]
            with self.assertRaises(ValueError):validate_contracts(IncrementContracts.model_validate(d),FunctionalIncrements.model_validate(self.d),ArchitectureProposal.model_validate(self.p),self.a)
    def test_unknown_requirement_rejected(self):
        self.c['contracts'][0]['criteria'][0]['requirement_ids']=['UNKNOWN']
        with self.assertRaises(ValueError):self.validate()
    def test_cannot_claim_pass_or_protection_from_generation(self):
        self.c['contracts'][0]['criteria'][0]['state']='passed'
        with self.assertRaises(ValueError):self.validate()
    def test_missing_exclusion_coverage_rejected(self):
        for c in self.c['contracts'][0]['criteria']:c['requirement_ids']=self.d['increments'][0]['requirement_ids']
        with self.assertRaises(ValueError):self.validate()
    def test_empty_observation_and_duplicate_criterion_rejected(self):
        self.c['contracts'][0]['criteria'][0]['expected']=''
        with self.assertRaises(ValueError):self.validate()
        self.setUp();self.c['contracts'][0]['criteria'].append(self.c['contracts'][0]['criteria'][0])
        with self.assertRaises(ValueError):self.validate()


if __name__=='__main__':unittest.main()
