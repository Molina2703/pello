import copy
import json
import unittest
from unittest.mock import patch

from athis_autopilot.product_planning import ProductPlanningCore
from tests.test_planning_graph import sample, proposal


def unpack(prompt):
    payload = json.loads(prompt.split('DATA JSON:\n', 1)[1])
    if 'pello_increment_context_encoding' in payload:
        table = payload['requirements']['requirements']
        payload['requirements']['requirements'] = [dict(zip(table['pello_requirement_columns'], row))
                                                       for row in table['pello_requirement_rows']]
        payload.pop('pello_increment_context_encoding')
    return payload


def baseline(phase, payload):
    with patch.object(ProductPlanningCore, '_increment_requirement_projection', return_value=None):
        return ProductPlanningCore._prompt(phase, payload)


class IncrementProjectionTests(unittest.TestCase):
    def setUp(self):
        analysis = sample().model_dump(mode='json')
        architecture = proposal(sample())
        nodes = architecture['nodes']
        # A shared requirement keeps separate node associations and contradictory
        # requirements retain their IDs, provenance and an explicit blocking issue.
        nodes[1]['requirement_ids'].append(nodes[0]['requirement_ids'][0])
        analysis['requirements'][0]['normalized'] = 'Refund the payment.'
        analysis['requirements'][1]['normalized'] = 'Do not refund the payment.'
        analysis['issues'][0]['kind'] = 'contradiction'
        analysis['issues'][0]['severity'] = 'blocking'
        analysis['issues'][0]['affected_requirement_ids'] = [r['requirement_id'] for r in analysis['requirements'][:2]]
        self.payload = {'project_id':'p', 'version':1, 'source_sha256':analysis['source_hash'],
            'requirements':analysis, 'execution_authorized':False,
            'architecture':{'nodes':nodes,'global_requirement_ids':architecture['global_requirement_ids']},
            'planning_objective':'Preserve all requirements', 'tool_catalog':{'python':'local'}}

    def test_reconstruction_associations_blockers_provenance_and_stability(self):
        original = copy.deepcopy(self.payload)
        for phase in ('plan-increments', 'plan-increments-r2', 'plan-increments-r3'):
            if phase != 'plan-increments': self.payload['reviewer_feedback'] = {'message':'preserve unresolved issue'}
            expected = copy.deepcopy(self.payload)
            prompt = ProductPlanningCore._prompt(phase, self.payload)
            self.assertIn('pello_increment_context_encoding', prompt)
            self.assertIn('depends_on and optional_dependencies refer to task IDs', prompt)
            self.assertIn('requirement depends_on refers to requirement IDs', prompt)
            self.assertLess(len(prompt), len(baseline(phase, self.payload)))
            self.assertEqual(unpack(prompt), expected)
            self.assertEqual(prompt, ProductPlanningCore._prompt(phase, self.payload))
            self.assertEqual(self.payload, expected)
        self.payload.pop('reviewer_feedback')
        self.assertEqual(self.payload, original)

    def test_conservative_fallback(self):
        for change in ('missing_id','unknown_requirement','unknown_dependency','duplicate_task',
                       'source_hash','unsupported_requirement','unsupported_top','marker','malformed_node','boolean_as_integer'):
            p = copy.deepcopy(self.payload)
            if change == 'missing_id': p['requirements']['requirements'][0].pop('requirement_id')
            elif change == 'unknown_requirement': p['architecture']['nodes'][0]['requirement_ids'] = ['missing']
            elif change == 'unknown_dependency': p['architecture']['nodes'][0]['depends_on'] = ['missing']
            elif change == 'duplicate_task': p['architecture']['nodes'][1]['task_id'] = p['architecture']['nodes'][0]['task_id']
            elif change == 'source_hash': p['source_sha256'] = 'b'*64
            elif change == 'boolean_as_integer': p['requirements']['requirements'][0]['approved_by_customer'] = 1
            elif change == 'unsupported_requirement': p['requirements']['requirements'][0]['extra'] = 'keep'
            elif change == 'unsupported_top': p['other'] = 'keep'
            elif change == 'marker': p['tool_catalog']['pello_table_rows'] = 'keep'
            else: p['architecture']['nodes'][0]['unexpected'] = 'keep'
            with self.subTest(change=change):
                self.assertEqual(ProductPlanningCore._prompt('plan-increments', p), baseline('plan-increments', p))

    def test_other_stages_and_no_savings_fall_back(self):
        self.assertEqual(ProductPlanningCore._prompt('plan-architecture', self.payload), baseline('plan-architecture', self.payload))
        p = copy.deepcopy(self.payload)
        p['requirements']['requirements'] = p['requirements']['requirements'][:1]
        self.assertEqual(ProductPlanningCore._prompt('plan-increments', p), baseline('plan-increments', p))

    def test_oversized_context_retains_existing_packing(self):
        p = copy.deepcopy(self.payload)
        p['planning_objective'] = 'x' * 55000
        try:
            expected = baseline('plan-increments', p)
        except ValueError:
            with self.assertRaises(ValueError): ProductPlanningCore._prompt('plan-increments', p)
        else:
            self.assertEqual(ProductPlanningCore._prompt('plan-increments', p), expected)


if __name__ == '__main__': unittest.main()
