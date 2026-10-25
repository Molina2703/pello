"""Expose the accepted authorization invariant at the model boundary."""
import unittest
from pydantic import ValidationError
from athis_autopilot.product_planning import RequirementAnalysis,RequirementDraft

class AuthorizationSchemaContractTests(unittest.TestCase):
    def requirement(self,category='authorization',required=True):
        return {'draft_id':'R1','source_ids':['SRC-local'],'normalized':'Enforce role permission for local edits.',
                'category':category,'origin':'customer_requirement','approved_by_customer':True,
                'priority':None,'depends_on':[],'acceptance_implications':['Unauthorized edits are rejected.'],
                'confidence':'high','uncertainty':'clear','external_dependencies':[],
                'external_effects':[],'authorization_required':required}

    def test_sdk_output_schema_explains_cross_field_guard_and_non_grant_meaning(self):
        schema=RequirementAnalysis.model_json_schema()
        description=schema['$defs']['RequirementDraft']['properties']['authorization_required'].get('description','')
        self.assertIn("category='authorization'",description)
        self.assertIn('must be true',description)
        self.assertIn('local role',description)
        self.assertIn('never grants',description)

    def test_local_authorization_rule_still_requires_true_without_external_effects(self):
        with self.assertRaises(ValidationError):RequirementDraft.model_validate(self.requirement(required=False))
        rule=RequirementDraft.model_validate(self.requirement())
        self.assertEqual(rule.external_effects,[])
        self.assertEqual(rule.category,'authorization')

    def test_ordinary_local_functionality_does_not_inherit_authorization_requirement(self):
        rule=RequirementDraft.model_validate(self.requirement(category='functional',required=False))
        self.assertFalse(rule.authorization_required)
