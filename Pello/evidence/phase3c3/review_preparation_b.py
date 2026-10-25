import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture

out=Path('evidence/phase3c3');revision=''
evidence_revision='-alias-proof' if 'alias-proof' in sys.argv else '-initial'
boundary=None
if evidence_revision:
    boundary=json.loads((out/'full-boundary-b-objective.json').read_text())
    boundary['common_native_command']=boundary['native_checks'][0]['command'][:-1]
    for record in boundary['native_checks']:record.pop('command')
    if 'alias-proof' in sys.argv:
        alias_proof=json.loads((out/'rubric-b-alias-proof.json').read_text())
        alias_proof['command_prefix_ref']='complete_boundary_verification.common_native_command except its last program element'
        alias_proof['program']=alias_proof['native_checks'][0]['command'][-2]
        for record in alias_proof['native_checks']:
            assert record['command'][:-2]==boundary['common_native_command'][:-1]
            record.pop('command')
        boundary['exact_declared_and_canonical_rubric_path_verification']=alias_proof
freeze=json.loads((out/('heldout-b-freeze'+revision+'.json')).read_text())
spec=(out/'heldout-b-spec.md').read_bytes();rubric=Path(freeze['private_rubric_path']).read_bytes()
fixture=HeldOutFixture.model_validate_json(rubric)
checks={'spec_hash':hashlib.sha256(spec).hexdigest()==freeze['specification_sha256'],
        'rubric_hash':hashlib.sha256(rubric).hexdigest()==freeze['rubric_sha256'],
        'source_quotes':all(not c.source_quote or c.source_quote in spec.decode() for c in fixture.rubric),
        'independent_capabilities':len(fixture.independent_capabilities)>=2,
        'threshold':fixture.minimum_critical_pass_fraction==1 and fixture.minimum_total_pass_fraction==0.9,
        'isolation_review':json.loads((out/'isolation/profile-review.json').read_text())['verdict']=='PASS',
        'native_boundary':all(x['passed'] for x in json.loads((out/'isolation/native-objective.json').read_text())),
        'no_planner_yet':True}
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=freeze['deny_read_roots']),timeout=480)
pid='phase3c3-review-b'
try:
    with core.db() as cx:checks['no_planner_yet']=cx.execute('select count(*) from pello_product_projects where project_id=?',('phase3c3-heldout-b',)).fetchone()[0]==0
    assert all(checks.values()),checks
    try:core.project_row(pid)
    except ValueError:
        folder=core.root/'projects'/pid
        if folder.exists():
            assert not list(folder.iterdir());folder.rmdir()  # Empty native deny-root placeholder, no project row.
        scope=out/'REVIEW_SCOPE.md';scope.write_text('# Independent Phase 3C-3 review\n\nReview frozen evaluation preparation, later original business source against actual autonomous plan, and final regression. Read-only; no implementation, no external effects.\n')
        remaining=int((datetime.fromisoformat('2026-10-26T00:45:00+00:00')-datetime.now(timezone.utc)).total_seconds()//60)
        core.create_project(scope,project_id=pid,duration_minutes=min(330,remaining))
    evidence={'objective':'Batch 1: independently assess novelty, relevance, completeness, frozen rubric and enforced isolation BEFORE Pello Planner is evaluated. Confirm realistic business problem with required features; rubric must permit alternative sound designs and distinguish critical from minor. No architecture, graph or manual increments may be supplied to Planner. Original development fixture was Vendor Return Desk; other known demos are appointment/clinic booking, chatbot/HMP, ADSA and numeric webhook QA. This new author session has received none of their plans. Planner gets only the specification; key stays in denied private directory, author artifacts, ledger and .codex transcripts. All those paths are denied. No Planner project exists yet. Reject incomplete or trivial evaluation.',
        'changed_files':['heldout-b-spec.md','private frozen rubric','heldout-b-freeze.json'],
        'diff':json.dumps({'fixture':fixture.model_dump(mode='json'),'freeze':freeze,'objective_checks':checks,
            'freeze_verification':{'specification':{'expected':freeze['specification_sha256'],'actual':hashlib.sha256(spec).hexdigest()},'rubric':{'expected':freeze['rubric_sha256'],'actual':hashlib.sha256(rubric).hexdigest()},'Planner_rows_query':'SELECT count(*) FROM pello_product_projects WHERE project_id=?','bindings':['phase3c3-heldout-b'],'Planner_rows_observed':0},
            'complete_boundary_verification':boundary,
            'native_checks':None if boundary else json.loads((out/'isolation/native-objective.json').read_text()),
            'native_transcripts':None if boundary else {p.name:p.read_text() for p in (out/'isolation').glob('native-*.log')},
            'runtime_profile_receipt':None if boundary else json.loads((out/'isolation/profile-live-probe.json').read_text())['profile_receipt'],
            'isolation_review':json.loads((out/'isolation/profile-review.json').read_text())},ensure_ascii=False,separators=(',',':')),
        'test_command':'Frozen input and native boundary checks',
        'test_exit_code':0,'tests_run':len(checks),'tests_passed':len(checks),'tests_failed':0,
        'scope_constraints':['No implementation or product test execution','Rubric frozen before Planner creation; cannot be changed after result','Separate author and Reviewer sessions; no private Planner reasoning','Native denial plus no-tools defense, no global configuration changes']}
    (out/('heldout-b-preparation-input'+revision+evidence_revision+'.json')).write_text(json.dumps(evidence,indent=2))
    review=core.review_engineering_increment(pid,'3c3-heldout-b-preparation'+revision+evidence_revision,evidence=evidence)
    (out/('heldout-b-preparation-review'+revision+evidence_revision+'.json')).write_text(json.dumps(review,indent=2))
    if review['verdict']=='PASS':
        accepted={'status':'ACCEPTED','freeze_sha256':hashlib.sha256((out/('heldout-b-freeze'+revision+'.json')).read_bytes()).hexdigest(),'checks':checks,'review':review,'created_at':datetime.now(timezone.utc).isoformat()}
        (out/('heldout-b-preparation-accepted'+revision+'.json')).write_text(json.dumps(accepted,indent=2))
    print(json.dumps(review,indent=2),flush=True)
finally:core.backend.close()
