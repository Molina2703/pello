import copy
import unittest
from athis_autopilot.planning_contracts import ModelDecisionProposal,validate_model_decision
from athis_autopilot.engines import CodexBlocked
from tests.test_product_planning import CAPABILITIES


def decision(effort='medium',model='gpt-6-luna'):
    return {'task_id':'INTAKE','responsibility':'coder','profile':{'model':model,'effort':effort},
        'complexity':'normal','risk':'medium','uncertainty':'low','context_requirements':'medium',
        'expected_turns':2,'selection_kind':'initial','previous_configuration':None,'failure_evidence':None,
        'exceptional_initial_sol':False,'decomposition_considered':True,
        'evidence_refs':['task:INTAKE'],'rationale':'A bounded local implementation with clear contracts is suitable for Luna.'}


class PlannedModelTests(unittest.TestCase):
    def check(self,d,**kwargs):return validate_model_decision(ModelDecisionProposal.model_validate(d),CAPABILITIES,budget_remaining=kwargs.get('budget',12))
    def test_initial_luna_efforts_are_adaptive(self):
        for effort in ('low','medium','high'):
            d=decision(effort);d['complexity']='complex' if effort=='high' else 'simple' if effort=='low' else 'normal'
            r=self.check(d);self.assertEqual(r['selected_reasoning_effort'],effort);self.assertTrue(r['verified_availability'])
    def test_justified_exceptional_initial_sol(self):
        d=decision('medium','gpt-6.1-sol');d.update(exceptional_initial_sol=True,complexity='complex',risk='high')
        self.assertEqual(self.check(d)['resolved_technical_model_id'],'gpt-6.1-sol')
    def test_unjustified_initial_sol_rejected(self):
        with self.assertRaises(ValueError):self.check(decision(model='gpt-6.1-sol'))
    def adapted(self,model='gpt-6-luna'):
        d=decision(model=model);d.update(selection_kind='adaptation',previous_configuration={'model':'gpt-6-luna','effort':'medium'},
            failure_evidence={'category':'implementation','severity':'minor','localized':True,'meaningful_progress':True,
                'actionable_diagnosis':True,'persistent_capability_gap':False,'recommendation':'continue',
                'evidence_refs':['review:ordinary-localized-failure']})
        return d
    def test_ordinary_fail_and_progress_allow_remaining_on_luna(self):
        for _ in range(4): self.assertEqual(self.check(self.adapted())['selected_model_profile'],'gpt-6-luna')
    def test_ordinary_fail_does_not_justify_sol(self):
        with self.assertRaises(ValueError):self.check(self.adapted('gpt-6.1-sol'))
    def test_persistent_evidence_allows_adaptive_sol_effort(self):
        d=self.adapted('gpt-6.1-sol');d['profile']['effort']='medium'
        d['failure_evidence'].update(meaningful_progress=False,persistent_capability_gap=True,recommendation='escalate',severity='major')
        self.assertEqual(self.check(d)['selected_reasoning_effort'],'medium')
    def test_replanning_and_decomposition_can_retain_luna(self):
        d=self.adapted();d['failure_evidence']['recommendation']='replan'
        self.assertFalse(self.check(d)['is_escalation'])
    def test_unavailable_model_or_effort_rejected(self):
        for model,effort in [('not-installed','medium'),('gpt-6-luna','ultra')]:
            d=decision();d['profile']={'model':model,'effort':effort}
            with self.assertRaises(ValueError):self.check(d)
        caps=copy.deepcopy(CAPABILITIES);caps['models']['gpt-6-luna']=['low']
        with self.assertRaises(CodexBlocked):validate_model_decision(ModelDecisionProposal.model_validate(decision()),caps,budget_remaining=12)
    def test_budget_rejection(self):
        with self.assertRaises(CodexBlocked):self.check(decision(),budget=0)
    def test_adaptation_requires_previous_configuration_and_evidence(self):
        d=decision();d['selection_kind']='adaptation'
        with self.assertRaises(ValueError):self.check(d)
    def test_machine_readable_record_and_no_execution_authorization(self):
        r=self.check(decision());self.assertEqual(r['task_id'],'INTAKE');self.assertIn('decision_timestamp',r)
        self.assertFalse(r['product_execution_authorized']);self.assertEqual(r['capability_snapshot']['models'],CAPABILITIES['models'])


if __name__=='__main__':unittest.main()
