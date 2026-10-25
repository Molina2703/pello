import unittest
from athis_autopilot.planning_contracts import ArchitectureProposal,FunctionalIncrements,validate_increments
from tests.test_planning_graph import sample,proposal
from tests.test_planning_increments import decomposition


class ToolRequirementTests(unittest.TestCase):
    def test_placeholder_is_not_a_tool(self):
        a=sample();p=ArchitectureProposal.model_validate(proposal(a));d=decomposition(a,proposal(a))
        d['increments'][0]['tools']=['Future-only-tooling-proposal']
        with self.assertRaises(ValueError):validate_increments(FunctionalIncrements.model_validate(d),p,a)
    def test_concrete_python_git_capabilities_remain_supported(self):
        a=sample();p=ArchitectureProposal.model_validate(proposal(a));d=decomposition(a,proposal(a))
        self.assertEqual(validate_increments(FunctionalIncrements.model_validate(d),p,a)['first_actionable'],'INTAKE')
    def test_declared_external_capability_does_not_grant_authorization(self):
        a=sample();p=ArchitectureProposal.model_validate(proposal(a));d=decomposition(a,proposal(a))
        d['increments'][-1]['tools']=['python','external_api']
        self.assertIn('authorization',validate_increments(FunctionalIncrements.model_validate(d),p,a)['blockers']['VENDOR'])


if __name__=='__main__':unittest.main()
