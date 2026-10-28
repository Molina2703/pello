"""Run ONE fresh held-out I variant; review before any further submission.

Usage: python evaluations/m1_4/run_variant.py A|B OUTPUT_DIR
OUTPUT_DIR must be new and outside this repository. Never retry an uncertain turn.
The independent reviewer must freeze expectations before either invocation.
"""
import hashlib
import json
import sys
import time
from pathlib import Path
from unittest.mock import patch

from athis_autopilot.ai_supervisor import SDKBackend
from athis_autopilot.model_policy import probe_capabilities, select_model
from athis_autopilot.pipeline_contracts import PipelinePolicy
from athis_autopilot.planning_contracts import ArchitectureProposal, FunctionalIncrements, validate_architecture, validate_increments
from athis_autopilot.product_planning import ProductPlanningCore, validate_planning_input

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'runtime/phase3c/projects/phase3c3-heldout-i/evidence/version-1'
FILES = {
    ROOT / 'evaluations/m1_4/EXPECTATIONS.md': 'fb59bd3cccf881371c32c3b279ed1f8634715d4c5cb9d067889d03936acb2c7f',
    ROOT / 'evidence/phase3c3/heldout-i-spec.md': 'd481313540b5f2959c4a8e10308262d08b920bb6dd8a33918ff48094ada91211',
    BASE / 'plan-increments/input.json': 'fae4e68a7e000fbb7553ac84172e92e1e4c606f3916cfbd3fcbcfd88c5a39659',
    BASE / 'planning/architecture.json': 'f0daea497fe626324f6e31aa111b931a80a43cdb167046405ec39ca579dbe000',
    BASE / 'plan-increments/codex_prompt.txt': '6f644ca89727165094639df7cd12a44be1880cf3454f69b92fd6471366114602',
}


def frozen_fixture():
    for path, digest in FILES.items():
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'Frozen artifact changed: {path}')
    payload = json.loads((BASE / 'plan-increments/input.json').read_text(encoding='utf-8'))
    arch = json.loads((BASE / 'planning/architecture.json').read_text(encoding='utf-8'))['proposal']
    analysis = validate_planning_input(payload['requirements'])
    parsed = ArchitectureProposal.model_validate(arch)
    validate_architecture(parsed, analysis)
    if payload['architecture'] != {k: arch[k] for k in ('nodes', 'global_requirement_ids')}:
        raise ValueError('Input architecture differs from validated architecture')
    with patch.object(ProductPlanningCore, '_increment_requirement_projection', return_value=None):
        baseline = ProductPlanningCore._prompt('plan-increments', payload)
    projected = ProductPlanningCore._prompt('plan-increments', payload)
    if baseline != (BASE / 'plan-increments/codex_prompt.txt').read_text(encoding='utf-8'):
        raise ValueError('Reconstructed baseline differs from original prompt')
    data = json.loads(projected.split('DATA JSON:\n', 1)[1])
    table = data['requirements']['requirements']
    data['requirements']['requirements'] = [dict(zip(table['pello_requirement_columns'], row)) for row in table['pello_requirement_rows']]
    data.pop('pello_increment_context_encoding')
    if data != payload or (len(baseline), len(projected)) != (53834, 46570):
        raise ValueError('Projection round trip or lengths differ from frozen fixture')
    return payload, parsed, analysis, baseline, projected


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ('A', 'B'):
        raise SystemExit(__doc__)
    label, output = sys.argv[1], Path(sys.argv[2]).resolve()
    if output.name != label or output == ROOT or ROOT in output.parents or output.exists():
        raise ValueError('Output must be a fresh A or B directory outside the repository matching the variant')
    payload, architecture, analysis, baseline, projected = frozen_fixture()
    caps = probe_capabilities()
    selection = select_model(PipelinePolicy(), caps, phase='plan-increments/planner', responsibility='planner')
    if (selection['model'], selection['effort']) != ('gpt-6.1-sol', 'high') or caps['remaining_percent'] is None or caps['remaining_percent'] <= 0:
        raise ValueError('Configured model/effort or measurable capacity unavailable')
    output.mkdir(parents=True, exist_ok=False)
    # Deny repository and sibling output access; this activates the native
    # read-only, network-disabled profile and checks it before submission.
    backend = SDKBackend(denied_read_roots=(ROOT, Path.home() / '.codex',
        Path.home() / 'AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/PelloEvaluation',
        output.parent / ('B' if label == 'A' else 'A')))
    started = time.monotonic()
    try:
        spec = output / 'spec.md'
        spec.write_bytes((ROOT / 'evidence/phase3c3/heldout-i-spec.md').read_bytes())
        core = ProductPlanningCore(output, backend=backend, timeout=300, capabilities=caps)
        core.create_project(spec, project_id=payload['project_id'], max_turns=1, duration_minutes=30)
        chosen = baseline if label == 'A' else projected
        core._prompt = lambda phase, value: chosen if phase == 'plan-increments' and value == payload else ProductPlanningCore._prompt(phase, value)
        response, turn = core._invoke(payload['project_id'], 1, 'plan-increments', 'planner', payload, FunctionalIncrements)
        result = {'variant': label, 'prompt_chars': len(chosen), 'usage': turn.get('usage'),
                  'elapsed_seconds': round(time.monotonic() - started, 2), 'model': selection['model'],
                  'effort': selection['effort'], 'thread_id': turn.get('thread_id'), 'turn_id': turn.get('turn_id')}
        try:
            result['validation'] = validate_increments(response, architecture, analysis)
        except ValueError as exc:
            result['validation_error'] = str(exc)
        (output / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        backend.close()


if __name__ == '__main__':
    main()
