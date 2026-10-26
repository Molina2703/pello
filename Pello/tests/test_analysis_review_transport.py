"""Regression for the preserved StageMark review-context rejection."""
import copy,json,unittest
from pathlib import Path
from athis_autopilot.product_planning import ProductPlanningCore

class AnalysisReviewTransportTests(unittest.TestCase):
    def payload(self):
        path=Path(__file__).resolve().parents[1]/'evidence/phase3c3/analysis-transport-correction/original-review-input.json'
        return json.loads(path.read_text(encoding='utf-8'))

    def unpack(self,value):
        if isinstance(value,dict):
            if set(value)=={'pello_table_columns','pello_table_rows'}:
                return [{key:self.unpack(cell) for key,cell in zip(value['pello_table_columns'],row)} for row in value['pello_table_rows']]
            return {key:self.unpack(cell) for key,cell in value.items()}
        if isinstance(value,list):return [self.unpack(cell) for cell in value]
        return value

    def test_preserved_rejection_round_trips_every_source_and_interpretation_field(self):
        for phase in ['review-analysis','review-analysis-r2']:
            with self.subTest(phase=phase):
                value=self.payload();original=copy.deepcopy(value)
                prompt=ProductPlanningCore._prompt(phase,value)
                self.assertLessEqual(len(prompt),55000)
                packed=json.loads(prompt.split('DATA JSON:\n',1)[1])
                self.assertIn('pello_context_encoding',packed)
                packed.pop('pello_context_encoding');restored=self.unpack(packed)
                restored.pop('context_encoding')
                lines=restored['original_product_specification_markdown'].splitlines()
                for segment in restored['source_segments']:
                    start,end=segment.pop('source_text_lines_ref')
                    segment['text']='\n'.join(lines[start-1:end]).strip()
                interpretation=restored['structured_interpretation']
                self.assertEqual(interpretation.pop('source_segments_ref'),'#/source_segments')
                interpretation['source_segments']=copy.deepcopy(restored['source_segments'])
                self.assertEqual(restored,original);self.assertEqual(value,original)

    def test_transport_marker_collision_rejects_without_mutating_canonical_input(self):
        value=self.payload();value['pello_table_rows']=['business data'];original=copy.deepcopy(value)
        with self.assertRaisesRegex(ValueError,'55,000'):ProductPlanningCore._prompt('review-analysis',value)
        self.assertEqual(value,original)

    def test_irreducible_review_rejects_without_losing_original_source(self):
        value=self.payload();value['additional_evidence']='x'*60000;original=copy.deepcopy(value)
        with self.assertRaisesRegex(ValueError,'55,000'):ProductPlanningCore._prompt('review-analysis',value)
        self.assertEqual(value,original)

    def test_small_review_retains_legacy_json_shape(self):
        value={'original_product_specification_markdown':'Small original source.','structured_interpretation':{'requirements':[]}}
        for phase in ['review-analysis','review-analysis-r2']:
            prompt=ProductPlanningCore._prompt(phase,value)
            self.assertEqual(json.loads(prompt.split('DATA JSON:\n',1)[1]),value)
