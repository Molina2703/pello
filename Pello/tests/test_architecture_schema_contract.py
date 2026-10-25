"""Model-facing architecture invariants must match unchanged Core enforcement."""
import unittest
from athis_autopilot.planning_contracts import ArchitectureProposal,validate_architecture
from tests.test_planning_graph import sample,proposal

class ArchitectureSchemaContractTests(unittest.TestCase):
    def test_schema_explains_global_category_restriction(self):
        field=ArchitectureProposal.model_json_schema()['properties']['global_requirement_ids']
        description=field.get('description','')
        for term in ['exclusion','constraint','non_functional','authorization','business_rule','work nodes']:
            self.assertIn(term,description)

    def test_schema_distinguishes_provided_inputs_from_availability_gates(self):
        field=ArchitectureProposal.model_json_schema()['$defs']['WorkNode']['properties']['required_resources']
        description=field.get('description','')
        for term in ['provided local','depends_on','unavailable','external']:
            self.assertIn(term,description)

    def test_business_rule_globalization_and_unknown_resource_guards_are_unchanged(self):
        a=sample();p=proposal(a)
        p['global_requirement_ids'].append(a.requirements[5].requirement_id)
        with self.assertRaisesRegex(ValueError,'Global constraints'):
            validate_architecture(ArchitectureProposal.model_validate(p),a)
        p=proposal(a);r=validate_architecture(ArchitectureProposal.model_validate(p),a)
        self.assertIn('resource:vendor-account',r['blockers']['VENDOR'])
        self.assertEqual(r['ready'],['INTAKE'])
