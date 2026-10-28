import hashlib
import json
import unittest

from evaluations.m1_2.run_pair import CASES, FROZEN_SHA256, variants
from athis_autopilot.product_planning import MarkdownSource


class EvaluationHarnessTests(unittest.TestCase):
    def test_frozen_cases_and_real_projection(self):
        raw = CASES.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), FROZEN_SHA256)
        cases = json.loads(raw)
        self.assertEqual(len(cases), 3)
        for case in cases:
            source = case['specification']
            payload = {'project_id': 'm12-eval', 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                       'product_specification_markdown': source,
                       'source_segments': [s.model_dump() for s in MarkdownSource.parse(source)]}
            before, after = variants(payload)
            self.assertLess(len(after), len(before))
            self.assertEqual(json.loads(before.split('DATA JSON:\n', 1)[1]), payload)
            self.assertEqual(before.split('DATA JSON:\n', 1)[0], after.split('DATA JSON:\n', 1)[0])

    def test_noncanonical_map_fails_before_inference(self):
        source = '# Heading\n\n' + 'Long statement. ' * 50
        segments = [s.model_dump() for s in MarkdownSource.parse(source)]
        segments[0]['text'] = 'wrong'
        with self.assertRaisesRegex(ValueError, 'did not activate'):
            variants({'product_specification_markdown': source, 'source_segments': segments})
