import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import athis_autopilot
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.planning_contracts import model_budget_summary

BASE=Path(athis_autopilot.__file__).resolve().parents[1]


class ModelRecoveryTests(unittest.TestCase):
    def test_aggregate_shortfall_is_explicit_without_fabricating_product_authorization(self):
        result=model_budget_summary([{'budget_assessment':{'estimated_coder_turns':1,'remaining_development_turns':6}} for _ in range(7)])
        self.assertEqual(result['estimated_coder_turns_total'],7);self.assertEqual(result['shortfall'],1)
        self.assertFalse(result['combined_estimate_fits_development_capacity']);self.assertFalse(result['product_execution_authorized'])
    def test_saved_decisions_resume_without_new_probe_or_sdk_call(self):
        saved=json.loads((BASE/'evidence/phase3c/3c2-b5/live-models.json').read_text(encoding='utf-8'))
        inc=json.loads((BASE/'evidence/phase3c/3c2-b3/live-increments-r2.json').read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory() as tmp:
            core=ProductPlanningCore(Path(tmp))
            core.create_project(BASE/'examples/phase3c/returns-desk.md',project_id='recovery')
            path=core.folder('recovery')/'evidence/version-1/planning/models.json';path.parent.mkdir(parents=True)
            path.write_text(json.dumps(saved),encoding='utf-8')
            with patch.object(core,'planner_input',return_value={}),patch.object(core,'planning_stage',return_value=inc),\
                 patch.object(core,'_capabilities_now',side_effect=AssertionError('unexpected catalog probe')),\
                 patch.object(core,'_invoke',side_effect=AssertionError('unexpected SDK replay')):
                result=core.propose_models('recovery')
                again=core.propose_models('recovery')
            self.assertEqual(result,again);self.assertEqual(result['proposal'],saved['proposal'])
            self.assertIn('aggregate_budget_assessment',result)


if __name__=='__main__':unittest.main()
