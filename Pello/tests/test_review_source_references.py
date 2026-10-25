"""Preserve a long source once, with exact recoverable source-map spans."""
import copy,json,unittest
from athis_autopilot.product_planning import ProductPlanningCore

class ReviewSourceReferenceTests(unittest.TestCase):
    def payload(self,newline='\n',corrupt=False):
        text='s'*6000;source=newline.join(['# Source','',text])
        segments=[{'source_id':'SRC-1','start_line':3,'end_line':3,'text':('z'*6000 if corrupt else text)}]
        return {'original_product_specification_markdown':source,'source_segments':segments,
            'structured_interpretation':{'source_segments':segments,'requirements':[{'normalized':'n'*45000}]}}

    def round_trip(self,value):
        before=copy.deepcopy(value);prompt=ProductPlanningCore._prompt('review-analysis',value)
        self.assertLessEqual(len(prompt),55000)
        p=json.loads(prompt.split('DATA JSON:\n',1)[1]);lines=p['original_product_specification_markdown'].splitlines()
        for segment in p['source_segments']:
            first,last=segment.pop('source_text_lines_ref')
            segment['text']='\n'.join(lines[first-1:last]).strip()
        self.assertEqual(p['structured_interpretation'].pop('source_segments_ref'),'#/source_segments')
        p['structured_interpretation']['source_segments']=p['source_segments'];p.pop('context_encoding')
        self.assertEqual(p,before);self.assertEqual(value,before)

    def test_large_review_payload_reconstructs_every_original_field(self):self.round_trip(self.payload())
    def test_crlf_source_preserves_canonical_segment_text(self):self.round_trip(self.payload('\r\n'))
    def test_nonmatching_source_text_is_not_hidden_behind_a_reference(self):
        with self.assertRaisesRegex(ValueError,'55,000'):
            ProductPlanningCore._prompt('review-analysis',self.payload(corrupt=True))
