"""Run one frozen, isolated M1.2 pair; inspect each pair before running another.

Usage: python evaluations/m1_2/run_pair.py CASE OUTPUT_DIRECTORY
OUTPUT_DIRECTORY must not already exist. It contains sensitive raw SDK evidence and
must remain outside the repository. Never retry an uncertain submission blindly.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

from athis_autopilot.ai_supervisor import SDKBackend
from athis_autopilot.model_policy import probe_capabilities, select_model
from athis_autopilot.pipeline_contracts import PipelinePolicy
from athis_autopilot.product_planning import (
    MarkdownSource, ProductPlanningCore, RequirementAnalysis, normalize_analysis,
    validate_planning_input,
)

FROZEN_SHA256 = '62671fa8cc373490fb4c8c7849fb27960676be5fe56582ae9edc30bea69bdf19'
CASES = Path(__file__).with_name('cases.json')


def variants(payload):
    projected = ProductPlanningCore._prompt('understand', payload)
    header, encoded = projected.split('DATA JSON:\n', 1)
    projected_data = json.loads(encoded)
    if 'context_encoding' not in projected_data:
        raise ValueError('Case did not activate the M1.1 projection')
    baseline = header + 'DATA JSON:\n' + json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
    rebuilt = dict(projected_data)
    rebuilt.pop('context_encoding')
    lines = rebuilt['product_specification_markdown'].splitlines()
    for segment in rebuilt['source_segments']:
        segment['text'] = '\n'.join(lines[segment['start_line']-1:segment['end_line']]).strip()
    if rebuilt != payload or baseline == projected:
        raise ValueError('Projection is not an exact reconstruction or variants do not differ')
    return baseline, projected


def main():
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    case_id, output = sys.argv[1], Path(sys.argv[2]).resolve()
    root = Path(__file__).resolve().parents[2]
    if output == root or root in output.parents:
        raise ValueError('Raw evaluation output must remain outside the repository')
    raw = CASES.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FROZEN_SHA256:
        raise ValueError('Frozen cases have changed; no inference permitted')
    case = next(c for c in json.loads(raw) if c['id'] == case_id)
    caps = probe_capabilities()
    selected = select_model(PipelinePolicy(), caps, phase='understand/planner', responsibility='planner')
    if (selected['model'], selected['effort']) != ('gpt-6.1-sol', 'high') or caps['remaining_percent'] is None:
        raise ValueError('Configured model or measurable remaining capacity is unavailable')
    output.mkdir(parents=True, exist_ok=False)
    spec = output / 'spec.md'
    spec.write_bytes(case['specification'].encode('utf-8'))
    summary = {'case': case_id, 'cases_sha256': FROZEN_SHA256, 'selection': selected, 'variants': {}}
    # Each variant uses a fresh backend, process, workspace, SQLite database and thread.
    for label in ('A', 'B'):
        backend = SDKBackend()
        started = time.monotonic()
        try:
            core = ProductPlanningCore(output / label, backend=backend, timeout=300, capabilities=caps)
            core.create_project(spec, project_id='m12-eval', max_turns=1, duration_minutes=30)
            version = core.version_row('m12-eval')
            segments = [s.model_dump() for s in MarkdownSource.parse(version['source_text'])]
            payload = {'project_id': 'm12-eval', 'source_sha256': version['source_hash'],
                       'product_specification_markdown': version['source_text'], 'source_segments': segments}
            baseline, projected = variants(payload)
            selected_prompt = baseline if label == 'A' else projected
            core._prompt = lambda phase, value: selected_prompt if phase == 'understand' and value == payload else ProductPlanningCore._prompt(phase, value)
            response, turn = core._invoke('m12-eval', 1, 'understand', 'planner', payload, RequirementAnalysis)
            item = {'elapsed_seconds': round(time.monotonic()-started, 2), 'prompt_chars': len(selected_prompt),
                    'baseline_chars': len(baseline), 'projected_chars': len(projected),
                    'usage': turn.get('usage'), 'thread_id': turn.get('thread_id'), 'turn_id': turn.get('turn_id')}
            try:
                accepted = normalize_analysis(response, MarkdownSource.parse(version['source_text']), version['source_hash'])
                validate_planning_input(accepted.model_dump(mode='json'))
                item['normalization'] = 'pass'
            except ValueError as exc:
                item['normalization'] = 'fail: ' + str(exc)
            summary['variants'][label] = item
            (output / 'summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding='utf-8')
        finally:
            backend.close()
    if summary['variants']['A']['thread_id'] == summary['variants']['B']['thread_id']:
        raise ValueError('Variants did not use independent sessions')
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
