"""Read-only offline diagnostics for persisted Pello planning evidence.

This module deliberately reports measurements only when the original serialized
artifact is present. Reconstructed prompts are never labeled as execution evidence.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from contextlib import closing
from collections import Counter
from pathlib import Path
from typing import Any

LIMIT = 55_000
HELDOUT = tuple("abcdefghi")


def _json_size(value: Any) -> int:
    return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _db_readonly(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA query_only=ON")
    return connection


def _source_metrics(source: str, analysis: dict[str, Any]) -> dict[str, int]:
    segments = analysis.get("source_segments", [])
    texts = [s.get("text", "") for s in segments if isinstance(s, dict)]
    hashes = [s.get("sha256") for s in segments if isinstance(s, dict)]
    occurrences = Counter(hashes)
    unique_text_by_hash = {}
    for digest, text in zip(hashes, texts):
        unique_text_by_hash.setdefault(digest, text)
    duplicate_chars = sum(map(len, texts)) - sum(map(len, unique_text_by_hash.values()))
    requirements = analysis.get("requirements", [])
    return {
        "specification_chars": len(source),
        "source_segment_count": len(segments),
        "source_segment_text_chars": sum(map(len, texts)),
        "duplicate_source_segment_count": sum(n - 1 for n in occurrences.values()),
        "duplicate_source_segment_text_chars": max(0, duplicate_chars),
        "requirement_count": len(requirements),
        "requirement_representation_chars": _json_size(requirements),
    }


def _stage_prompts(project_root: Path, specification_chars: int) -> list[dict[str, Any]]:
    base = project_root / "evidence" / "version-1"
    stages = []
    if not base.is_dir():
        return stages
    for prompt in sorted(base.glob("*/codex_prompt.txt")):
        size = len(prompt.read_text(encoding="utf-8"))
        stages.append({"stage": prompt.parent.name, "chars": size,
                       "chars_over_specification": max(0, size - specification_chars),
                       "specification_to_prompt_ratio": round(size / max(1, specification_chars), 2),
                       "over_limit": size > LIMIT, "evidence": "persisted_original_prompt"})
    return stages


def _stage_inputs(project_root: Path) -> list[dict[str, Any]]:
    """Measure journaled input envelopes; these are not mislabeled as prompts."""
    base = project_root / "evidence" / "version-1"
    records = []
    if not base.is_dir():
        return records
    for input_path in sorted(base.glob("*/input.json")):
        raw = input_path.read_text(encoding="utf-8")
        value = json.loads(raw)
        segment_lists: list[list[dict[str, Any]]] = []

        def visit(item: Any) -> None:
            if isinstance(item, dict):
                for key, child in item.items():
                    if key == "source_segments" and isinstance(child, list):
                        segment_lists.append(child)
                    visit(child)
            elif isinstance(item, list):
                for child in item:
                    visit(child)

        visit(value)
        repeated_chars = 0
        duplicate_map_count = 0
        if len(segment_lists) > 1:
            canonical = json.dumps(segment_lists[0], ensure_ascii=False, separators=(",", ":"))
            for duplicate in segment_lists[1:]:
                if json.dumps(duplicate, ensure_ascii=False, separators=(",", ":")) == canonical:
                    duplicate_map_count += 1
                    repeated_chars += sum(len(s.get("text", "")) for s in duplicate if isinstance(s, dict))
        records.append({"stage": input_path.parent.name, "chars": len(raw),
                        "source_segment_maps": len(segment_lists),
                        "exact_duplicate_source_map_count": duplicate_map_count,
                        "duplicated_source_segment_text_chars": repeated_chars,
                        "evidence": "persisted_input_envelope_not_original_prompt"})
    return records


def _evaluation(evidence: Path, letter: str) -> dict[str, Any] | None:
    path = evidence / f"heldout-{letter}-evaluation.json"
    if not path.is_file():
        return None
    value = _read_json(path)
    return {"verdict": value.get("verdict"),
            "critical_failures": value.get("critical_failures", []),
            "failure_evidence": value.get("failure_evidence")}


def _planning_replay(project_root: Path, analysis_json: str | None) -> dict[str, Any]:
    """Replay stored planning validators and manifest readiness when artifacts exist."""
    evidence = project_root / "evidence" / "version-1" / "planning"
    result: dict[str, Any] = {"artifacts": [], "validation": "insufficient_artifacts"}
    if evidence.is_dir():
        result["artifacts"] = sorted(p.name for p in evidence.glob("*.json"))
    manifest_path = evidence / "execution-manifest.json"
    if manifest_path.is_file():
        from .pipeline import IncrementalPipeline

        manifest = _read_json(manifest_path)
        result["manifest_scheduler"] = IncrementalPipeline.inspect_planned_manifest(manifest)
        result["manifest_dependencies"] = {item["task_id"]: item.get("depends_on", [])
                                           for item in manifest.get("increments", [])}
        result["validation"] = "existing_scheduler_replayed"
    # Existing architecture and increment validators are used only when their
    # complete typed inputs are persisted. Missing pieces are explicit.
    if analysis_json:
        from .product_planning import AcceptedAnalysis
        from .planning_contracts import (ArchitectureProposal, FunctionalIncrements,
                                         validate_architecture, validate_increments)

        analysis = AcceptedAnalysis.model_validate_json(analysis_json)
        architecture_path = evidence / "architecture.json"
        if not architecture_path.is_file():
            architecture_path = project_root / "evidence" / "version-1" / "plan-architecture" / "codex_result.json"
        increments_path = next((evidence / name for name in
                                ("increments-r1.json", "increments.json", "increments-current.json")
                                if (evidence / name).is_file()), evidence / "increments.json")
        if architecture_path.is_file():
            raw = _read_json(architecture_path)
            if "final_response" in raw and isinstance(raw["final_response"], str):
                raw = json.loads(raw["final_response"])
            raw = raw.get("proposal", raw)
            try:
                architecture = ArchitectureProposal.model_validate(raw)
                graph = validate_architecture(architecture, analysis)
                result["architecture_validation"] = graph
                req_to_tasks: dict[str, list[str]] = {}
                for node in architecture.nodes:
                    for req_id in node.requirement_ids:
                        req_to_tasks.setdefault(req_id, []).append(node.task_id)
                result["requirement_dependencies"] = {
                    req.requirement_id: req.depends_on for req in analysis.requirements if req.depends_on}
                result["issue_requirement_associations"] = {
                    issue.issue_id: issue.affected_requirement_ids for issue in analysis.issues
                    if issue.affected_requirement_ids}
                result["issue_increment_associations"] = {
                    issue.issue_id: sorted({task for req_id in issue.affected_requirement_ids
                                            for task in req_to_tasks.get(req_id, [])})
                    for issue in analysis.issues if issue.affected_requirement_ids}
                result["task_dependencies"] = {node.task_id: node.depends_on for node in architecture.nodes
                                                if node.depends_on}
                result["validation"] = "existing_validators_replayed"
                if increments_path.is_file():
                    increment_raw = _read_json(increments_path)
                    increments = FunctionalIncrements.model_validate(increment_raw.get("proposal", increment_raw))
                    result["increment_validation"] = validate_increments(increments, architecture, analysis)
            except (ValueError, TypeError) as exc:
                result["deterministic_failure"] = str(exc)
                result["validation"] = "existing_validator_reproduced_failure"
    return result


def _find_parcelproof_artifact(evidence: Path, runtime: Path) -> Path | None:
    """Find a specifically named persisted plan without guessing from narratives."""
    candidates = sorted((path for root in (evidence, runtime) for path in root.rglob("*.json")
                         if path.name in {"execution-manifest.json", "plan-r1.json"}
                         or ("parcelproof" in path.name.casefold() and "plan" in path.name.casefold())),
                        key=lambda path: str(path).casefold())
    for path in candidates:
        try:
            value = _read_json(path)
        except (OSError, UnicodeError, json.JSONDecodeError):
            continue
        if not isinstance(value, dict):
            continue
        serialized = json.dumps(value, ensure_ascii=False).casefold()
        current = value
        if isinstance(current.get("plan"), dict):
            current = current["plan"]
        manifest = current.get("manifest", current)
        increments = manifest.get("increments", []) if isinstance(manifest, dict) else []
        ids = {item.get("task_id") for item in increments if isinstance(item, dict)}
        has_actual_graph = ids == {f"W0{i}" for i in range(1, 9)}
        if has_actual_graph and "p-7" in serialized and "parcelproof" in serialized:
            return path
    return None


def inspect_parcelproof(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {"status": "missing_persisted_plan", "reproduced": False,
                "detail": "No persisted ParcelProof planning manifest was found; C13 cannot be reproduced from this workspace."}
    from .pipeline import IncrementalPipeline

    plan = _read_json(path)
    plan = plan.get("plan", plan)
    manifest = plan.get("manifest", plan)
    replay = IncrementalPipeline.inspect_planned_manifest(manifest, completed={"W01", "W02", "W03"})
    by_id = {item["task_id"]: item for item in manifest.get("increments", [])}
    blockers = replay["blockers"]
    return {"status": "replayed", "reproduced": True,
            "completed": replay["completed"], "ready": replay["ready"],
            "w04_blockers": blockers.get("W04"), "w05_blockers": blockers.get("W05"),
            "w05_depends_on_w04": "W04" in by_id.get("W05", {}).get("depends_on", []),
            "w05_immediately_ready": "W05" in replay["ready"],
            "w04_classification": "unnecessary_whole_increment_block_from_P7_dispute; objective preserves other-parcel schedule work",
            "w05_classification": "independent_unnecessary_recovery_issue_blocker; also dependency-blocked by W04",
            "w06_w08_blockers": {w: blockers.get(w) for w in ("W06", "W07", "W08")},
            "w06_w08_reason": {
                "W06": "Conditional positive P-7 review requires an authoritative conveyancer resolution; the plan forbids choosing either claim or fabricating resolution.",
                "W07": "External lodgement requires a confirmed agency contract, real access and firm permissions, plus separate exact-package principal authorization.",
                "W08": "Recovery after an unknown external outcome requires documented resolution evidence, resolver responsibility and duplicate-lodgement semantics, in addition to W07 gates.",
            },
            "scheduler_semantics": "IncrementalPipeline.inspect_planned_manifest"}


def diagnose(database: Path, evidence: Path, runtime: Path) -> dict[str, Any]:
    reports = []
    with closing(_db_readonly(database)) as connection:
        for letter in HELDOUT:
            project_id = f"phase3c3-heldout-{letter}"
            project = connection.execute(
                "SELECT p.project_id,p.current_version,v.source_text,v.analysis "
                "FROM pello_product_projects p JOIN pello_product_versions v "
                "ON v.project_id=p.project_id AND v.version=p.current_version "
                "WHERE p.project_id=?", (project_id,)).fetchone()
            history = connection.execute(
                "SELECT analysis_json FROM pello_product_analysis_history "
                "WHERE project_id=? ORDER BY version DESC,revision DESC LIMIT 1", (project_id,)).fetchone()
            analysis_json = (history["analysis_json"] if history else
                             project["analysis"] if project else None)
            analysis = json.loads(analysis_json) if analysis_json else None
            project_root = runtime / "phase3c" / "projects" / project_id
            metrics = _source_metrics(project["source_text"], analysis) if project and analysis else None
            prompt_source_chars = len(project["source_text"]) if project else 0
            persisted_prompt_paths = _stage_prompts(project_root, prompt_source_chars)
            persisted_inputs = _stage_inputs(project_root)
            reports.append({
                "evaluation": project_id,
                "specification_chars": len(project["source_text"]) if project else None,
                "persisted_analysis_chars": len(analysis_json) if analysis_json else None,
                "analysis_available": analysis is not None,
                "metrics": metrics,
                "stage_prompts": persisted_prompt_paths,
                "stage_input_envelopes": persisted_inputs,
                "stages_without_exact_prompt": "Not reconstructable from original execution evidence.",
                "evaluation_result": _evaluation(evidence, letter),
                "planning_replay": _planning_replay(project_root, analysis_json) if project else
                                   {"validation": "missing_sqlite_project"},
            })
    missing_analysis = [r["evaluation"] for r in reports if not r["analysis_available"]]
    missing_evaluations = [r["evaluation"] for r in reports if r["evaluation_result"] is None]
    prompt_measurements = [s for r in reports for s in r["stage_prompts"]]
    input_measurements = [s for r in reports for s in r["stage_input_envelopes"]]
    spec_chars = [r["metrics"]["specification_chars"] for r in reports if r["metrics"]]
    analysis_ratios = [r["persisted_analysis_chars"] / r["metrics"]["specification_chars"]
                       for r in reports if r["metrics"] and r["persisted_analysis_chars"]]
    requirement_chars = [r["metrics"]["requirement_representation_chars"]
                         for r in reports if r["metrics"]]
    parcel_path = _find_parcelproof_artifact(evidence, runtime)
    first_failure = next(({
        "evaluation": row["evaluation"],
        "failure": row["planning_replay"]["deterministic_failure"],
        "evaluation_evidence": row["evaluation_result"],
    } for row in reports if row["planning_replay"].get("deterministic_failure")), None)
    return {
        "mode": "offline_read_only",
        "database": str(database),
        "limit_chars": LIMIT,
        "heldout_evaluations": reports,
        "analysis_count": len(reports) - len(missing_analysis),
        "missing_analyses": missing_analysis,
        "missing_evaluations": missing_evaluations,
        "measured_stage_prompt_count": len(prompt_measurements),
        "measured_stage_input_envelope_count": len(input_measurements),
        "context_amplification_findings": {
            "specification_chars_range": [min(spec_chars), max(spec_chars)] if spec_chars else None,
            "persisted_analysis_to_spec_ratio_range": [round(min(analysis_ratios), 2),
                                                        round(max(analysis_ratios), 2)] if analysis_ratios else None,
            "requirement_representation_chars_range": [min(requirement_chars), max(requirement_chars)]
            if requirement_chars else None,
            "largest_measured_prompt_chars": max((p["chars"] for p in prompt_measurements), default=None),
            "review_input_duplicate_maps_chars": [min(s["duplicated_source_segment_text_chars"]
                                                      for s in input_measurements
                                                      if s["duplicated_source_segment_text_chars"]),
                                                   max(s["duplicated_source_segment_text_chars"]
                                                       for s in input_measurements
                                                       if s["duplicated_source_segment_text_chars"])]
            if any(s["duplicated_source_segment_text_chars"] for s in input_measurements) else None,
            "interpretation": "Major measured sources include large requirement representations and repeated source maps in journaled inputs; these measurements do not apportion every original prompt character.",
        },
        "stage_input_source_duplication": [
            {"evaluation": r["evaluation"], **item}
            for r in reports for item in r["stage_input_envelopes"]
            if item["duplicated_source_segment_text_chars"]],
        "measured_stage_prompts_over_limit": [
            {"evaluation": r["evaluation"], **s}
            for r in reports for s in r["stage_prompts"] if s["over_limit"]],
        "stage_limit_failures_from_evaluations": [
            {"evaluation": r["evaluation"], "reported_stage": _reported_limit_stage(r["evaluation_result"]["critical_failures"]),
             "original_prompt_chars": None, "evidence_kind": "historical_evaluation_not_original_prompt",
             "failures": r["evaluation_result"]["critical_failures"]}
            for r in reports if r["evaluation_result"] and any(
                "55,000" in str(failure) or "55000" in str(failure)
                or "oversized duplicated review context" in str(failure).casefold()
                for failure in r["evaluation_result"]["critical_failures"])],
        "first_reproducible_deterministic_failure": first_failure,
        "deterministic_replay_summary": {
            row["evaluation"]: {
                "validation": row["planning_replay"].get("validation"),
                "first_actionable": (row["planning_replay"].get("increment_validation", {}).get("first_actionable")
                                     or row["planning_replay"].get("manifest_scheduler", {}).get("first_actionable")
                                     or row["planning_replay"].get("architecture_validation", {}).get("ready", [None])[0]),
                "deadlock": ("reproduced" if any(word in str(row["planning_replay"].get("deterministic_failure", "")).casefold()
                                                    for word in ("cycle", "topological", "no ready"))
                             else "not detected in available validated graph"),
                "issue_requirement_associations": row["planning_replay"].get("issue_requirement_associations", {}),
                "issue_increment_associations": row["planning_replay"].get("issue_increment_associations", {}),
                "requirement_dependencies": row["planning_replay"].get("requirement_dependencies", {}),
                "task_dependencies": row["planning_replay"].get("task_dependencies", {}),
                "manifest_dependencies": row["planning_replay"].get("manifest_dependencies", {}),
                "manifest_blockers": row["planning_replay"].get("manifest_scheduler", {}).get("blockers", {}),
                "validated_graph_blockers": row["planning_replay"].get("architecture_validation", {}).get("blockers", {}),
                "increment_states": row["planning_replay"].get("increment_validation", {}).get("states", {}),
                "blocker_classes": _classify_blockers(
                    row["planning_replay"].get("manifest_scheduler", {}).get("blockers", {}),
                    row["planning_replay"].get("architecture_validation", {}).get("blockers", {})),
            } for row in reports if row["planning_replay"].get("validation") != "insufficient_artifacts"
        },
        "parcelproof_c13": inspect_parcelproof(parcel_path),
        "limitations": [
            "Prompt sizes are measured only from persisted codex_prompt.txt files; missing prompts are not reconstructed.",
            "SQLite and artifact values are read-only; this command does not execute planning or inference.",
        ],
    }


def _classify_blockers(*blocker_maps: dict[str, list[str]]) -> dict[str, list[str]]:
    """Separate unresolved specification/safety gates from dependency propagation."""
    classes: dict[str, set[str]] = {
        "unresolved_specification_or_resource_or_authorization": set(),
        "dependency_propagation": set(),
        "other_planning_blockers": set(),
    }
    for blocker_map in blocker_maps:
        for task_id, blockers in blocker_map.items():
            for blocker in blockers:
                if blocker.startswith("dependency:"):
                    classes["dependency_propagation"].add(f"{task_id}:{blocker}")
                elif blocker.startswith(("specification:", "resource:")) or blocker == "authorization":
                    classes["unresolved_specification_or_resource_or_authorization"].add(
                        f"{task_id}:{blocker}")
                else:
                    classes["other_planning_blockers"].add(f"{task_id}:{blocker}")
    return {key: sorted(values) for key, values in classes.items()}


def _reported_limit_stage(failures: list[str]) -> str | None:
    text = " ".join(failures).casefold()
    if "contract planning context" in text:
        return "plan-contracts"
    if "increment planning context" in text:
        return "plan-increments"
    if ("review context" in text or "review-analysis" in text
            or "interpretation-review context" in text or "oversized duplicated review context" in text):
        return "review-analysis"
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=Path("evidence/phase3c3/checkpoint-108-jobs.sqlite3"))
    parser.add_argument("--evidence", type=Path, default=Path("evidence/phase3c3"))
    parser.add_argument("--runtime", type=Path, default=Path("runtime"))
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)
    report = diagnose(args.database, args.evidence, args.runtime)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        _print_report(report)
    return 0


def _print_report(report: dict[str, Any]) -> None:
    print("Pello offline planning diagnostics")
    print(f"Persisted analyses: {report['analysis_count']}/9; missing: {', '.join(report['missing_analyses']) or 'none'}")
    print(f"Exact stage prompts measured: {report['measured_stage_prompt_count']}; "
          f"persisted prompts over {LIMIT}: {len(report['measured_stage_prompts_over_limit'])}")
    amplification = report["context_amplification_findings"]
    print(f"Context amplification: analysis/spec={amplification['persisted_analysis_to_spec_ratio_range']}x; "
          f"requirement JSON={amplification['requirement_representation_chars_range']} chars; "
          f"largest exact prompt={amplification['largest_measured_prompt_chars']:,} chars")
    for row in report["heldout_evaluations"]:
        metrics = row["metrics"]
        if metrics:
            print(f"{row['evaluation']}: spec={metrics['specification_chars']:,} chars, "
                  f"analysis={row['persisted_analysis_chars']:,} chars, "
                  f"requirements={metrics['requirement_count']} ({metrics['requirement_representation_chars']:,} chars), "
                  f"segment-copy={metrics['duplicate_source_segment_text_chars']:,} chars")
        else:
            print(f"{row['evaluation']}: specification={row['specification_chars']} chars; analysis unavailable")
        for stage in row["stage_prompts"]:
            print(f"  {stage['stage']}: {stage['chars']:,} chars measured, "
                  f"{stage['chars_over_specification']:,} above spec ({stage['specification_to_prompt_ratio']}x spec)")
    failed = report["stage_limit_failures_from_evaluations"]
    if failed:
        print("Historical over-limit failures (reported stage; original prompt length unavailable):")
        for item in failed:
            print(f"  {item['evaluation']}: {item['reported_stage'] or 'stage unresolved'}")
    first = report["first_reproducible_deterministic_failure"]
    if first:
        details = first["evaluation_evidence"]["critical_failures"]
        print(f"Earliest replayed deterministic failure: {first['evaluation']} - {first['failure']}; "
              f"evaluation cause: {details[0] if details else 'not recorded'}")
    for evaluation, replay in report["deterministic_replay_summary"].items():
        if replay["manifest_blockers"]:
            print(f"{evaluation}: scheduler first action={replay['first_actionable']}; "
                  f"planning blockers preserved={len(replay['manifest_blockers'])}")
    for item in report["stage_input_source_duplication"]:
        print(f"{item['evaluation']} {item['stage']}: journaled input has "
              f"{item['duplicated_source_segment_text_chars']:,} duplicate source-segment chars "
              f"(input envelope, not original submitted prompt)")
    c13 = report["parcelproof_c13"]
    if c13["reproduced"]:
        print(f"ParcelProof C13: W01-W03 completed; W04 blocked by {c13['w04_blockers']}; "
              f"W05 also blocked by {c13['w05_blockers']} and depends on W04 "
              f"(immediately ready={c13['w05_immediately_ready']}); "
              f"W06-W08 retain their dispute, external authorization/access and recovery blockers.")
    else:
        print(f"ParcelProof C13: {c13['status']} - {c13['detail']}")


if __name__ == "__main__":
    raise SystemExit(main())
