import json
from pathlib import Path
import unittest
from athis_autopilot.n8n_qa import QAContract, validate_blueprint, check_cases, verify_remote
class DraftAcceptance(unittest.TestCase):
    def setUp(self):
        self.contract=QAContract.model_validate_json(Path(__file__).with_name('contract.json').read_text())
        self.source=json.loads(Path('workflow.json').read_text())
    def test_safe_source_structure(self): validate_blueprint(self.source,self.contract)
    def test_independent_contract_cases(self): self.assertTrue(all(c['passed'] for c in check_cases(self.source,self.contract)))
    def test_remote_definition_matches_source(self):
        evidence=json.loads(Path('remote-draft.json').read_text()); verify_remote(evidence['workflow'],self.source,self.contract)
    def test_actual_identity_version_and_mcp_exposure(self):
        e=json.loads(Path('remote-draft.json').read_text())
        self.assertTrue(e['workflow']['id']); self.assertTrue(e['workflow']['versionId'])
        self.assertEqual(e['workflow']['id'],e['workflow_id'])
        self.assertFalse(e['workflow']['active']); self.assertTrue(e['mcp_available']); self.assertTrue(e['official_validation']['valid'])
    def test_real_manual_execution_results(self):
        e=json.loads(Path('remote-draft.json').read_text()); self.assertEqual(len(e['manual_cases']),2)
        for case in e['manual_cases']:
            self.assertTrue(case['execution_id']); self.assertEqual(case['observed_output'],case['expected']); self.assertTrue(case['passed'])
