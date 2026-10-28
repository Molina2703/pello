import copy
import json
import unittest

from athis_autopilot.product_planning import MarkdownSource, ProductPlanningCore


def unpack(prompt):
    value = json.loads(prompt.split('DATA JSON:\n', 1)[1])
    if 'context_encoding' in value:
        value.pop('context_encoding')
        lines = value['product_specification_markdown'].splitlines()
        for segment in value['source_segments']:
            segment['text'] = '\n'.join(lines[segment['start_line'] - 1:segment['end_line']]).strip()
    return value


class ContextProjectionTests(unittest.TestCase):
    def payload(self):
        source = ('# Rules\n\nThe customer may cancel before payment. ' * 12 +
                  '\n\nThe customer may cancel after payment. ' * 12 +
                  '\n\nPayment must be refunded.\n\nPayment must not be refunded.\n')
        segments = [s.model_dump() for s in MarkdownSource.parse(source)]
        return {'product_specification_markdown': source, 'source_segments': segments,
                'requirements': [{'id': 'R1', 'source_ids': [segments[0]['source_id']],
                                  'depends_on': ['R2'], 'acceptance': ['exact'], 'blocking': True},
                                 {'id': 'R2', 'source_ids': [segments[0]['source_id']],
                                  'constraints': ['no external effect']}],
                'issues': [{'contradiction': True, 'affected': ['R1', 'R2']}]}

    def test_complete_round_trip_and_determinism(self):
        payload = self.payload()
        original = copy.deepcopy(payload)
        first = ProductPlanningCore._prompt('understand', payload)
        self.assertEqual(first, ProductPlanningCore._prompt('understand', payload))
        self.assertEqual(unpack(first), original)
        self.assertEqual(payload, original)
        self.assertIn('context_encoding', json.loads(first.split('DATA JSON:\n', 1)[1]))

    def test_invalid_or_unresolved_source_map_is_not_projected(self):
        for change in ('wrong_text', 'missing', 'wrong_id', 'extra', 'marker', 'boolean_line', 'mixed_key'):
            payload = self.payload()
            if change == 'wrong_text': payload['source_segments'][0]['text'] = 'different'
            elif change == 'missing': payload['source_segments'][0].pop('start_line')
            elif change == 'wrong_id': payload['source_segments'][0]['source_id'] = 'unresolved'
            elif change == 'extra': payload['source_segments'][0]['source_text_lines_ref'] = [1, 2]
            elif change == 'boolean_line': payload['source_segments'][0]['start_line'] = True
            elif change == 'mixed_key': payload['source_segments'][0][1] = 'malformed'
            else: payload['context_encoding'] = 'original data'
            result = json.loads(ProductPlanningCore._prompt('understand', payload).split('DATA JSON:\n', 1)[1])
            self.assertEqual(result, json.loads(json.dumps(payload)))

    def test_other_stages_are_unchanged(self):
        payload = self.payload()
        result = json.loads(ProductPlanningCore._prompt('other', payload).split('DATA JSON:\n', 1)[1])
        self.assertEqual(result, payload)

    def test_heading_whitespace_falls_back_without_losing_text(self):
        source = '# Heading   \n\n' + 'A long statement. ' * 60
        payload = {'product_specification_markdown': source,
                   'source_segments': [s.model_dump() for s in MarkdownSource.parse(source)]}
        result = json.loads(ProductPlanningCore._prompt('understand', payload).split('DATA JSON:\n', 1)[1])
        self.assertEqual(result, payload)

    def test_mixed_line_endings_round_trip(self):
        source = '# Heading\r\n\r\n' + 'First rule. ' * 60 + '\r' + 'Second rule. ' * 60
        payload = {'product_specification_markdown': source,
                   'source_segments': [s.model_dump() for s in MarkdownSource.parse(source)]}
        prompt = ProductPlanningCore._prompt('understand', payload)
        self.assertIn('context_encoding', json.loads(prompt.split('DATA JSON:\n', 1)[1]))
        self.assertEqual(unpack(prompt), payload)
