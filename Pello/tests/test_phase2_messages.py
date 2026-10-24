import json
import unittest
from pydantic import ValidationError
from athis_autopilot.messages import SupervisorDecision, VerificationResult, parse_response, correlate


class MessageTests(unittest.TestCase):
    def decision(self):
        return {'project_id': 'project1', 'task_id': 'T001', 'decision': 'BLOCKED',
                'tasks': [], 'reasoning_summary': 'Missing requirements', 'next_action': 'Clarify the requirements'}

    def test_valid_structured_decision(self):
        parsed = parse_response(SupervisorDecision, json.dumps(self.decision()))
        self.assertEqual(parsed.decision, 'BLOCKED')

    def test_malformed_json_rejected(self):
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, '{bad')

    def test_missing_field_rejected(self):
        data = self.decision(); del data['next_action']
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, json.dumps(data))

    def test_unknown_field_rejected(self):
        data = self.decision(); data['override_verification'] = True
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, json.dumps(data))

    def test_unknown_action_rejected(self):
        data = self.decision(); data['decision'] = 'DEPLOY'
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, json.dumps(data))

    def test_nonempty_reason_required(self):
        data = self.decision(); data['reasoning_summary'] = ' '
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, json.dumps(data))

    def test_markdown_fences_rejected(self):
        with self.assertRaises(ValidationError): parse_response(SupervisorDecision, '```json\n' + json.dumps(self.decision()) + '\n```')

    def test_correlation(self):
        message = parse_response(SupervisorDecision, json.dumps(self.decision()))
        for project, task in (('other', 'T001'), ('project1', 'other')):
            with self.subTest(project=project, task=task), self.assertRaises(ValueError): correlate(message, project, task)

    def test_false_passing_verification_rejected(self):
        for executed, passed, failed, skipped in ((0, 0, 0, 0), (2, 1, 1, 0), (2, 1, 0, 1), (2, 2, 1, 0)):
            with self.subTest(executed=executed, failed=failed, skipped=skipped), self.assertRaises(ValidationError):
                VerificationResult(project_id='p1', task_id='T1', verification_status='PASSED',
                    tests_executed=executed, passed=passed, failed=failed, skipped=skipped,
                    evidence_paths=[], error_summary='')

    def test_output_size_bound(self):
        with self.assertRaises(ValueError): parse_response(SupervisorDecision, 'x' * 64001)
