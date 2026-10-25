import json
from pathlib import Path
import unittest
from athis_autopilot.n8n_qa import QAContract, verify_remote
class PublishedAcceptance(unittest.TestCase):
    def test_published_qa_evidence(self):
        e=json.loads(Path('remote-published.json').read_text())
        c=QAContract.model_validate_json(Path(__file__).with_name('contract.json').read_text())
        verify_remote(e['workflow'],json.loads(Path('workflow.json').read_text()),c)
        self.assertTrue(e['workflow']['active']); self.assertTrue(e['verified'])
        self.assertEqual(e['workflow']['activeVersionId'],e['reviewed_version'])
        self.assertEqual(e['workflow']['id'],e['workflow_id'])
        self.assertEqual([x['name'] for x in e['http_cases']],['valid','invalid-type','negative','repeat-valid'])
        for case in e['http_cases']:
            self.assertEqual(case['status'],case['expected_status'])
            self.assertEqual(case['body'],case['expected_body'])
            self.assertTrue(case['passed'])
        self.assertTrue(e['execution_results'])
        for execution in e['execution_results']:
            self.assertTrue(execution['id']); self.assertTrue(execution['successful'])
            self.assertEqual(execution['workflow_id'],e['workflow_id'])
