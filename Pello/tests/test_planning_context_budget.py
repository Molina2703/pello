"""Regression for held-out context overflow and a never-submitted reservation."""
import copy,json,tempfile,unittest
from pathlib import Path
from athis_autopilot.product_planning import ProductPlanningCore,EngineeringReview
from test_product_planning import FakeBackend,CAPABILITIES

class PlanningContextBudgetTests(unittest.TestCase):
    def test_unreducible_context_rejected_before_turn_reservation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);spec=root/'spec.md';spec.write_text('# Product\n\nKeep a local record.\n')
            backend=FakeBackend();core=ProductPlanningCore(root/'runtime',backend=backend,capabilities=CAPABILITIES)
            core.create_project(spec,project_id='context-budget')
            with self.assertRaisesRegex(ValueError,'55,000'):
                core._invoke('context-budget',1,'oversized','reviewer',{'data':'x'*60000},EngineeringReview)
            self.assertEqual(core.project_row('context-budget')['used_turns'],0)
            with core.db() as cx:self.assertEqual(cx.execute('select count(*) from pello_product_operations').fetchone()[0],0)
            self.assertEqual(backend.calls,[])

    def test_duplicate_source_map_can_be_factored_losslessly_under_same_limit(self):
        segments=[{'source_id':'SRC-123','text':'x'*6000}]
        payload={'original_product_specification_markdown':'x'*6000,'source_segments':segments,
                 'structured_interpretation':{'source_segments':segments,'requirements':[{'normalized':'n'*38000}]}}
        original=copy.deepcopy(payload)
        prompt=ProductPlanningCore._prompt('review-analysis',payload)
        self.assertLessEqual(len(prompt),55000)
        packed=json.loads(prompt.split('DATA JSON:\n',1)[1])
        self.assertEqual(packed['structured_interpretation'].pop('source_segments_ref'),'#/source_segments')
        packed['structured_interpretation']['source_segments']=packed['source_segments']
        packed.pop('context_encoding')
        self.assertEqual(packed,original)
        self.assertEqual(payload,original)

    def test_distinct_source_maps_are_never_replaced_by_a_reference(self):
        payload={'source_segments':[{'text':'a'*30000}],
                 'structured_interpretation':{'source_segments':[{'text':'b'*30000}]}}
        with self.assertRaisesRegex(ValueError,'55,000'):
            ProductPlanningCore._prompt('review-analysis',payload)

    def test_small_historical_context_encoding_is_unchanged(self):
        value={'source_segments':[{'text':'small'}],'structured_interpretation':{'source_segments':[{'text':'small'}]}}
        prompt=ProductPlanningCore._prompt('review-analysis',value)
        self.assertEqual(json.loads(prompt.split('DATA JSON:\n',1)[1]),value)
