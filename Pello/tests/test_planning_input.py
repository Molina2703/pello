"""Frozen Batch 1 acceptance: use the real accepted Phase 3C-1 output."""
import copy
import json
import unittest
from pathlib import Path
from athis_autopilot.product_planning import validate_planning_input

BASE = Path(__file__).resolve().parents[1]


class PlanningInputTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((BASE/'evidence/phase3c/3c1-final-analysis.json').read_text(encoding='utf-8'))

    def test_real_analysis_round_trips_without_semantic_changes(self):
        self.assertEqual(validate_planning_input(self.data).model_dump(mode='json'), self.data)

    def test_missing_fields_and_malformed_input_fail(self):
        for data in ({}, 'not-json', {**self.data, 'requirements': []}):
            with self.assertRaises(ValueError): validate_planning_input(data)

    def test_duplicate_ids_and_conflicting_definitions_fail(self):
        self.data['requirements'].append(copy.deepcopy(self.data['requirements'][0]))
        self.data['requirements'][-1]['normalized'] = 'Conflicting definition'
        with self.assertRaises(ValueError): validate_planning_input(self.data)

    def test_invalid_source_dependency_issue_and_assumption_references_fail(self):
        cases = [('requirements','source_ids'),('requirements','depends_on'),
                 ('issues','affected_requirement_ids'),('assumptions','related_requirement_ids')]
        for collection, field in cases:
            data=copy.deepcopy(self.data); data[collection][0][field]=['unknown']
            with self.subTest(collection=collection, field=field):
                with self.assertRaises(ValueError): validate_planning_input(data)

    def test_source_segment_tampering_fails(self):
        self.data['source_segments'][0]['text'] += 'changed'
        with self.assertRaises(ValueError): validate_planning_input(self.data)

    def test_blockers_assumptions_and_exclusions_survive(self):
        actual=validate_planning_input(self.data)
        self.assertEqual(sum(i.severity=='blocking' for i in actual.issues),6)
        self.assertEqual(sum(i.severity=='non_blocking' for i in actual.issues),2)
        self.assertEqual(len(actual.assumptions),2)
        self.assertTrue(all(a.approval_status=='not_customer_approved' for a in actual.assumptions))
        self.assertTrue(any(r.category=='exclusion' for r in actual.requirements))


if __name__ == '__main__': unittest.main()
