import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from athis_autopilot.planning_diagnostics import (
    LIMIT, _reported_limit_stage, _source_metrics, _stage_prompts,
    _db_readonly, inspect_parcelproof,
)


class PlanningDiagnosticsTests(unittest.TestCase):
    def test_source_and_requirement_sizes_count_duplicate_segment_text(self):
        source = "A source"
        analysis = {
            "source_segments": [
                {"sha256": "same", "text": "A source"},
                {"sha256": "same", "text": "A source"},
                {"sha256": "other", "text": "tail"},
            ],
            "requirements": [{"requirement_id": "R1", "normalized": "Collect"}],
        }
        result = _source_metrics(source, analysis)
        self.assertEqual(result["specification_chars"], len(source))
        self.assertEqual(result["source_segment_text_chars"], 20)
        self.assertEqual(result["duplicate_source_segment_count"], 1)
        self.assertEqual(result["duplicate_source_segment_text_chars"], 8)
        self.assertEqual(result["requirement_representation_chars"], len(
            json.dumps(analysis["requirements"], ensure_ascii=False, separators=(",", ":"))))

    def test_prompt_sizes_are_measured_from_saved_original_file_only(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            stage = project / "evidence/version-1/plan-architecture"
            stage.mkdir(parents=True)
            prompt = "x" * (LIMIT + 1)
            (stage / "codex_prompt.txt").write_text(prompt, encoding="utf-8")
            measured = _stage_prompts(project, 100)
        self.assertEqual(measured[0]["chars"], LIMIT + 1)
        self.assertTrue(measured[0]["over_limit"])
        self.assertEqual(measured[0]["evidence"], "persisted_original_prompt")

    def test_input_envelope_duplicate_map_is_not_reported_as_prompt(self):
        from athis_autopilot.planning_diagnostics import _stage_inputs

        segments = [{"source_id": "SRC-000000000000", "text": "original span"}]
        other = [{"source_id": "SRC-111111111111", "text": "different span"}]
        payload = {"source_segments": segments, "structured_interpretation": {"source_segments": segments},
                   "other_evidence": {"source_segments": other}}
        with tempfile.TemporaryDirectory() as temp:
            input_path = Path(temp) / "evidence/version-1/review-analysis/input.json"
            input_path.parent.mkdir(parents=True)
            input_path.write_text(json.dumps(payload), encoding="utf-8")
            measured = _stage_inputs(Path(temp))
        self.assertEqual(measured[0]["duplicated_source_segment_text_chars"], len("original span"))
        self.assertEqual(measured[0]["exact_duplicate_source_map_count"], 1)
        self.assertEqual(measured[0]["evidence"], "persisted_input_envelope_not_original_prompt")

    def test_limit_failure_stage_is_inferred_from_original_evaluation_text(self):
        self.assertEqual(_reported_limit_stage(["Contract planning context exceeds55000"]), "plan-contracts")
        self.assertEqual(_reported_limit_stage(["Source-plus-source-map review context exceeded 55,000"]), "review-analysis")
        self.assertEqual(_reported_limit_stage(["Oversized duplicated review context"]), "review-analysis")
        self.assertIsNone(_reported_limit_stage(["Unrelated architecture issue"]))

    def test_blocker_report_keeps_legitimate_gates_separate_from_dependencies(self):
        from athis_autopilot.planning_diagnostics import _classify_blockers

        result = _classify_blockers({"W04": ["specification:ISS-1"], "W05": ["dependency:W04"]},
                                    {"W07": ["authorization", "resource:agency"]})
        self.assertEqual(result["unresolved_specification_or_resource_or_authorization"],
                         ["W04:specification:ISS-1", "W07:authorization", "W07:resource:agency"])
        self.assertEqual(result["dependency_propagation"], ["W05:dependency:W04"])

    def test_database_connection_is_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "evidence.sqlite3"
            cx = sqlite3.connect(path)
            try:
                cx.execute("CREATE TABLE sample(value TEXT)")
                cx.commit()
            finally:
                cx.close()
            with closing(_db_readonly(path)) as cx:
                with self.assertRaises(sqlite3.OperationalError):
                    cx.execute("INSERT INTO sample VALUES('mutation')")

    def test_parcelproof_absence_is_reported_without_synthetic_replay(self):
        result = inspect_parcelproof(None)
        self.assertEqual(result["status"], "missing_persisted_plan")
        self.assertFalse(result["reproduced"])
        self.assertIn("cannot be reproduced", result["detail"])

    def test_hypothetical_manifest_uses_existing_scheduler_dependency_gate(self):
        def increment(task_id, *, depends=(), blockers=()):
            return {"task_id": task_id, "specification": task_id, "inputs": ["input"],
                    "outputs": ["output"], "components": [f"src/{task_id}.py"],
                    "acceptance_criteria": ["verify"], "depends_on": list(depends),
                    "suite": f"tests/{task_id}", "expected_tests": 1,
                    "planning_blockers": list(blockers)}

        manifest = {"architecture_constraints": ["planning only"], "tools": [], "increments": [
            increment("W01"), increment("W02", depends=("W01",)),
            increment("W03", depends=("W02",)),
            increment("W04", depends=("W03",), blockers=("specification:P-7 dispute",)),
            increment("W05", depends=("W04",), blockers=("planning:independent issue",)),
            increment("W06", depends=("W05",), blockers=("authorization",)),
            increment("W07", depends=("W06",)), increment("W08", depends=("W07",)),
        ]}
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "parcelproof-plan.json"
            path.write_text(json.dumps({"manifest": manifest}), encoding="utf-8")
            result = inspect_parcelproof(path)
        self.assertEqual(result["completed"], ["W01", "W02", "W03"])
        self.assertNotIn("W04", result["ready"])
        self.assertIn("specification:P-7 dispute", result["w04_blockers"])
        self.assertTrue(result["w05_depends_on_w04"])
        self.assertNotIn("W05", result["ready"])
        self.assertIn("planning:independent issue", result["w05_blockers"])
        self.assertNotIn("W06", result["ready"])
        self.assertEqual(result["scheduler_semantics"], "IncrementalPipeline.inspect_planned_manifest")


if __name__ == "__main__":
    unittest.main()
