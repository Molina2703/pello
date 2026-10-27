"""One new independent case; eight prior held-out failures remain consumed."""
import hashlib, json, sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture

out = Path('evidence/phase3c3')
assert json.loads((out/'authorization-extension-114.json').read_text())['cumulative_sdk_limit'] == 114
assert json.loads((out/'continuation114-recovery-verification.json').read_text())['focused_pass']
prior = json.loads((out/'heldout-h-freeze-v2.json').read_text())
private = Path(prior['private_rubric_path']).parents[1]/'phase3c3-i'
private.mkdir(exist_ok=True)
roots = prior['deny_read_roots']+[str(Path('runtime/phase3c/projects/phase3c3-review-i').resolve())]
Path(roots[-1]).mkdir(exist_ok=True)
core = ProductPlanningCore(Path('runtime/phase3c'), backend=SDKBackend(denied_read_roots=roots), timeout=600)
try:
    core._role_instructions = lambda role: 'You are the independent held-out evaluation author. Create a new realistic business specification and private outcome rubric. You have not received the current Planner reasoning or implementation. Do not use tools. Do not create a technical plan, graph, increments or expected architecture. Return exact schema JSON.'
    data, raw = core._invoke('phase3c3-author', 1, 'author-heldout-i', 'tester', {
        'objective': 'Create ONE entirely fresh small-business scenario in a substantially different operational domain from Vendor Return Desk, CanalShare irrigation, ArchiveLedger digital-record custody, KilnBook timber production, FolioPay royalty settlement, StackProof air-emissions compliance, AssemblyCount meeting voting, StageMark bicycle-race classification and CueConform subtitle adaptation after video edits, and HMP/ADSA/chatbot demos. Do not re-skin those cases. Make realistic partial planning possible while disputed or unauthorized portions remain blocked. Avoid unnecessary length and artificial complexity; preserve all mandatory evaluation attributes.',
        'required_attributes': ['Multiple functional capabilities and meaningful business rules', 'Operational constraints and explicit exclusions', 'Dependencies and at least two independently actionable local branches', 'External integration with missing critical information or a genuine contradiction', 'Nonblocking reversible assumptions recorded without customer approval', 'Permission-sensitive external operation with no execution authorization', 'Observable completion conditions including concrete normal, error and boundary examples'],
        'format': 'Complete natural-language business source, target 4000-5500 characters, within the 8500-character schema ceiling; finish every sentence and section. No technical decomposition or implementation guidance. Private rubric 20-28 criteria. Exact source_quote for source-based criteria. Every mandatory outcome is critical. Include at least one explicitly minor clarity/presentation criterion which does not invent mandatory behavior or require a particular document layout. Permit alternative sound architectures and storage choices. All critical must pass and overall fraction >=0.9. Proposed product acceptance criteria are not executed tests. Evaluation id phase3c3-heldout-i-v1.',
        'resources': {'local_synthetic_data': True, 'local_python_sqlite_git_capabilities': True, 'external_credentials': None, 'external_accounts': None, 'external_authorizations': []},
    }, HeldOutFixture)
    spec = data.specification_markdown.encode('utf-8')
    fixture = data.model_dump(mode='json')
    rubric = json.dumps(fixture, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')
    checks = {'exact_quotes': all(not c.source_quote or c.source_quote in data.specification_markdown for c in data.rubric),
              'minor_exists': any(c.severity=='minor' for c in data.rubric),
              'novel_source_hash': all(hashlib.sha256(spec).hexdigest()!=json.loads(p.read_text())['specification_sha256'] for p in out.glob('heldout-*-freeze*.json')),
              'correct_identity': data.evaluation_id=='phase3c3-heldout-i-v1'}
    (out/'heldout-i-author-checks.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
    assert all(checks.values()), checks
    assert not (out/'heldout-i-freeze.json').exists() and not (private/'rubric.json').exists()
    (out/'heldout-i-spec.md').write_bytes(spec)
    (private/'rubric.json').write_bytes(rubric)
    freeze = {k: prior[k] for k in ('threshold','objective_check_registry','critical_failure_conditions')}
    freeze.update(evaluation_id=data.evaluation_id, version=1, created_at=datetime.now(timezone.utc).isoformat(),
        specification_sha256=hashlib.sha256(spec).hexdigest(), rubric_sha256=hashlib.sha256(rubric).hexdigest(),
        private_rubric_path=str(private/'rubric.json'), deny_read_roots=roots,
        author_thread_id=raw['thread_id'], author_turn_id=raw['turn_id'],
        critical_criteria=sum(c.severity=='critical' for c in data.rubric), total_criteria=len(data.rubric),
        status='FROZEN_BEFORE_PLANNER', fresh_case_reason='Eight original cases remain FAIL. New source and rubric independently authored without Planner outputs or an expected technical solution; no Planner project exists yet.')
    (out/'heldout-i-freeze.json').write_text(json.dumps(freeze, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'evaluation_id':data.evaluation_id,'product_name':data.product_name,'source_characters':len(data.specification_markdown),'critical_criteria':freeze['critical_criteria'],'total_criteria':freeze['total_criteria'],'source_sha256':freeze['specification_sha256'],'rubric_sha256':freeze['rubric_sha256']}, indent=2), flush=True)
finally:
    core.backend.close()
