"""Independent closure review; accepted-plan transition remains in existing Core."""
import hashlib,json,sqlite3,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend

out=Path('evidence/phase3c3')
def read(name):return json.loads((out/name).read_text(encoding='utf-8'))
evaluation=read('heldout-e-evaluation.json');assert evaluation['verdict']=='PASS'
reg=read('final-regression.json');integrity=read('final-integrity.json');protected=read('final-protected.json')
assert reg['exit_code']==0 and reg['tests_run']>=236
assert integrity['historical_hashes_matching']==integrity['historical_hashes_checked']==1493
assert all(p['exit_code']==0 and p['source_hashes_intact'] and p['protected_copy_hash_intact'] for p in protected)
assert integrity['first_28_sdk_operation_rows_unchanged'] and integrity['original_projects_preserved']
assert integrity['sqlite_integrity']=='ok' and not integrity['stop_set']
assert integrity['frozen_objective_script_intact'] and all(p['matches'] for p in integrity['new_protected_test_sources'])
assert all(p['commit_present'] for p in integrity['checkpoint_commits'])
f=read('heldout-e-freeze.json');pid='phase3c3-heldout-e';rid='phase3c3-review-e'
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    recovered=core.reconstruct_plan(pid);assert recovered['plan_sha256']==evaluation['plan_sha256']
    with core.db() as c:
        auth=[dict(r) for r in c.execute('select * from pello_product_run_authorizations order by rowid')]
        statuses=[dict(r) for r in c.execute('select status,count(*) as count from pello_product_operations group by status')]
        charges=c.execute('select count(*) from pello_product_operations').fetchone()[0]
        sessions=[dict(r) for r in c.execute('select project_id,role,thread_id from pello_sessions where project_id in (?,?)',(pid,rid))]
    assert charges<75 and datetime.now(timezone.utc)<datetime.fromisoformat('2026-10-26T03:30:00+00:00')
    diff=subprocess.run(['git','diff','c1bb076e7059100f0c4b5abf623625d2843f0be2','--','athis_autopilot','tests'],capture_output=True,text=True,encoding='utf-8',check=True).stdout
    grading={p:(out/p).read_text(encoding='utf-8') for p in ['objective_checks_e.py','review_semantics_e.py','pack_review.py']}
    checkpoints={k:v for k,v in integrity.items() if k!='checkpoint_commits'}
    checkpoints['checkpoint_git_objects_verified']=len(integrity['checkpoint_commits'])
    packet={
      'mission':'Final independent Phase 3C review. You previously received the ORIGINAL StackProof source and exact frozen rubric in this same independent Reviewer session, and independently scored every criterion. No private Planner reasoning is supplied. Evaluate the original Phase 3C objectives, untouched held-out evidence, objective gates, relevant production/test diff, corrections and preservation. Do not modify implementation. Objective FAIL cannot be overridden. Acceptance is planning-level only; no business product or its tests were implemented. V1-20 is not complete. Phase 3D must not start.',
      'original_phase_3c_objectives':['Interpret structured business specifications with traceable requirements, exclusions, contradictions, missing critical information and unapproved assumptions','Generate architecture, coherent dependency graph, functional increments, technical contracts and proposed acceptance criteria without manual technical translation','Select typed models/efforts adaptively using actual backend availability and task risk/context/budget, without rigid escalation','Persist and reconstruct through existing SQLite and PipelineManifest; identify actionable independent work and keep blocked/unauthorized work ineligible','Demonstrate genuine generalization on an independent frozen unseen scenario using actual SDK, with enforced rubric isolation','Preserve C1 and C2 acceptance, STOP/budget enforcement, protected suites and historical FAILs; independent final review required'],
      'prior_acceptance':{'C1':'ACCEPTED historical: 13 interpretation items, 16 source segments, 6 blockers, 2 nonblocking issues, 2 assumptions; 28 targeted/154 full at that milestone','C2':'ACCEPTED historical: six batches, 217 full/63 protected, 1493 integrity, accepted plan digest 7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87; original final report retained in Git','C2_current_reconstruction':read('architecture-contract-correction/accepted-checkpoint.json')},
      'frozen_evaluation':f,'preparation':read('heldout-e-preparation-accepted.json'),
      'objective':read('heldout-e-objective.json'),'semantic_verdict':read('heldout-e-semantic-review.json'),'deterministic_semantic_gate':evaluation,
      'production_and_test_git_diff':diff,'evaluation_grading_source':grading,
      'regression':reg,'protected':protected,'integrity':checkpoints,
      'correction_reviews':{p:read(p+'/review.json') for p in ['context-correction','authorization-correction','source-context-correction','architecture-contract-correction']},
      'isolation_review':read('isolation/profile-review.json'),
      'original_failures_preserved':{p:read(p) for p in ['heldout-a-evaluation.json','heldout-b-evaluation.json','heldout-c-evaluation.json','heldout-d-evaluation.json']},
      'authorization':{'records':auth,'latest_explicit_user_grant':read('authorization-extension-75.json'),'charged_before_this_review':charges,'statuses':statuses,'session_independence':sessions,'STOP':False,'external_business_operations':0,'business_Coder_calls':0,'historical_charge_never_submitted':1,'no_counter_reset':True},
      'scope_limitations':['One successful new held-out case can support scoped planning generalization, not universal reliability','Four initial blind FAILs remain FAIL; localized corrections were engineering changes, not autonomous self-repair','Criteria are proposed: no business tests generated, protected or executed','No external integrations, production mutations, customer data or n8n operations','No full enterprise product delivery; no V1-20 completion; no Phase 3D'],
      'checkpoint_before_planner':read('batch1-e-checkpoint.json')}
    evidence={'objective':'Final independent Phase 3C closure review against original objectives and untouched held-out evidence. PASS only if all mandatory objective gates pass and no critical semantic or independence defect remains.',
      'changed_files':['athis_autopilot/{ai_supervisor,codex_worker,engines,planning_contracts,product_planning}.py','six protected Phase 3C-3 regression sources','frozen evaluation artifacts and local harnesses'],
      'diff':json.dumps(packet,ensure_ascii=False,separators=(',',':')),'test_command':'Full unittest + six protected suites + hash/SQLite/checkpoint/restart gates',
      'test_exit_code':0,'tests_run':reg['tests_run'],'tests_passed':reg['tests_run'],'tests_failed':0,
      'scope_constraints':[{'plan_sha256':recovered['plan_sha256'],'regression':reg,'protected_suites_intact':True},'Planning acceptance only; no implementation authorization; no Phase 3D','Frozen rubric cannot be changed and objective FAIL cannot be overridden']}
    length=len(json.dumps(evidence,ensure_ascii=False));print('final_review_characters',length,flush=True)
    (out/'final-review-input.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    assert length<=50000,'Keep evidence; reduce repetition losslessly before invoking, never drop a failed gate'
    increment='3c3-final-heldout-e'
    review=core.review_engineering_increment(rid,increment,evidence=evidence)
    (out/'final-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8');print(json.dumps(review,indent=2),flush=True)
    assert review['verdict']=='PASS','No acceptance without independent final PASS'
    accepted=core.approve_plan(pid,review_project_id=rid,review_phase='engineering-review-'+increment)
    status=core.inspect_plan(pid)
    assert accepted['approval']=='ACCEPTED' and status['execution_authorized'] is False
    (out/'accepted-plan-checkpoint.json').write_text(json.dumps({'accepted':accepted,'inspection':status,'at':datetime.now(timezone.utc).isoformat(),'review':review},indent=2),encoding='utf-8')
finally:core.backend.close()
