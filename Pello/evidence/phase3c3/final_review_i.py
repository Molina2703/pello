"""Hash-bound independent closure; use the existing Core approval transition."""
import hashlib,json,sqlite3,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
class ClosureReceipt(BaseModel):
    model_config=ConfigDict(extra='forbid')
    received:Literal[True]
    status:Literal['RECEIVED_NOT_A_VERDICT']
    notes:str=Field(max_length=400)
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256((out/p).read_bytes()).hexdigest()
evaluation=read('heldout-i-evaluation.json');assert evaluation['verdict']=='PASS'
reg=read('final-i-regression.json');integrity=read('final-i-integrity.json');protected=read('final-i-protected.json')
assert reg['exit_code']==0 and reg['tests_run']>=257
assert integrity['historical_hashes_matching']==integrity['historical_hashes_checked']==1493
assert all(p['exit_code']==0 and p['source_hashes_intact'] and p['protected_copy_hash_intact'] for p in protected)
assert integrity['first_28_sdk_operation_rows_unchanged'] and integrity['original_projects_preserved']
assert integrity['sqlite_integrity']=='ok' and not integrity['stop_set']
assert integrity['frozen_objective_script_intact'] and all(p['matches'] for p in integrity['new_protected_test_sources'])
assert all(p['commit_present'] for p in integrity['checkpoint_commits'])
assert read('heldout-i-actual-isolation-audit.json')['verdict']=='PASS'
f=read('heldout-i-freeze.json');pid='phase3c3-heldout-i';rid='phase3c3-review-i'
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    recovered=core.reconstruct_plan(pid);assert recovered['plan_sha256']==evaluation['plan_sha256']
    with core.db() as c:
        auth=[dict(r) for r in c.execute('select * from pello_product_run_authorizations order by rowid')]
        statuses=[dict(r) for r in c.execute('select status,count(*) as count from pello_product_operations group by status')]
        charges=c.execute('select count(*) from pello_product_operations').fetchone()[0]
        code_op=dict(c.execute("select * from pello_product_operations where project_id=? and phase='engineering-review-3c3-final-code-i'",(rid,)).fetchone())
    assert charges<114 and datetime.now(timezone.utc)<datetime.fromisoformat(auth[-1]['deadline'])
    diff=subprocess.check_output(['git','diff','--unified=0','c1bb076e7059100f0c4b5abf623625d2843f0be2','--','athis_autopilot','tests'],text=True,encoding='utf-8')
    code=read('final-i-code-review.json');assert code['review']['verdict']=='PASS'
    assert code['diff_sha256']==hashlib.sha256(diff.encode()).hexdigest()
    assert code['input_sha256']==sha('final-i-code-review-input.json')
    assert json.loads(code_op['response'])['thread_id']==code['part1_thread_id']==evaluation['review_thread_id']
    old=sqlite3.connect(Path('evidence/phase3c3/checkpoint-88-jobs.sqlite3').resolve().as_uri()+'?mode=ro',uri=True);old.row_factory=sqlite3.Row
    old_ops=[dict(x) for x in old.execute('select * from pello_product_operations order by rowid')];old.close()
    with core.db() as c:current=[dict(x) for x in c.execute('select * from pello_product_operations order by rowid limit 88')]
    assert old_ops==current and len(current)==88
    histories=[]
    for row in auth:
        grant=json.loads(row['grant_json'])
        histories.append({'id':row['id'],'max_turns':row['max_turns'],'deadline':row['deadline'],'user_authorization':grant.get('user_authorization'),'complete_grant_json_sha256':hashlib.sha256(row['grant_json'].encode()).hexdigest()})
    failures={}
    for letter in 'abcdefgh':
        name=f'heldout-{letter}-evaluation.json';value=read(name);assert value['verdict']=='FAIL'
        failures[letter]={'verdict':value['verdict'],'complete_original_record_sha256':sha(name),'original_record':value}
    grading={name:(out/name).read_text(encoding='utf-8') for name in ['objective_checks_i.py','review_semantics_i.py','pack_review.py','audit_blind_i.py','run_planning_i.py','verify_actual_batches_i.py']}
    packet={
      'mission':'Final independent Phase 3C closure review. In this SAME Reviewer session you received the original ParcelProof source and frozen rubric, graded every semantic criterion, and reviewed the complete production/test Git diff in ordered parts. Combine those actual artifacts with the complete closure evidence below. No private Planner reasoning is supplied. No code modifications. Objective FAIL cannot be overridden. Planning-only acceptance: no enterprise product, product tests, publication or V1-20 completion. Do not begin Phase3D.',
      'original_phase_3c_objectives':['Traceable specification understanding, exclusions, contradictions, missing information and unapproved assumptions','Autonomous architecture/DAG, coherent functional increments, contracts and objective proposed criteria','Typed adaptive models/efforts justified by actual availability, risk/context/budget, no rigid ladder','Existing SQLite and PipelineManifest reconstruction/readiness without manual technical translation; blocked and unauthorized work remain ineligible','Fresh unseen independent frozen business source, private rubric isolated, all critical and >=90% total PASS','Preserve C1/C2, protected tests, original FAILs, STOP/budgets/checkpoints and independent final review'],
      'prior_acceptance':{'C1':'ACCEPTED at its historical checkpoint; 13 interpretation items,16 source segments,6 blocking/2 nonblocking issues,2 assumptions;28 targeted/154 full tests then','C2':'ACCEPTED: six sequential batches,217 full/63 protected tests,1493 integrity hashes; original reports and results retained','C2_current_reconstruction':read('continuation114-recovery-verification.json')},
      'frozen_evaluation':f,'preparation':read('heldout-i-preparation-accepted.json'),'pre_Planner_checkpoint':read('batch1-i-checkpoint.json'),'pre_Planner_Git_checkpoint':read('batch1-i-git-checkpoint.json'),
      'actual_isolation':read('heldout-i-actual-isolation-audit.json'),'actual_contract_batching':read('heldout-i-actual-contract-batching.json'),
      'complete_plan_identity':{'plan_sha256':recovered['plan_sha256'],'stage_hashes':recovered['plan']['stage_hashes'],'manifest_sha256':core.plan_digest(recovered['plan']['manifest'])},
      'objective':read('heldout-i-objective.json'),'semantic':read('heldout-i-semantic-review.json'),'deterministic_semantic_gate':evaluation,
      'complete_diff_review':code,
      'regression':reg,'protected':protected,'integrity':integrity,
      'all_eight_original_failures':failures,
      'architecture_recovery_real_run':{'initial_valid':not (core.folder(pid)/'evidence/version-1/planning/architecture-initial-rejection.json').exists(),'note':'No artificial error injected. If initial valid, bounded recovery remains controlled-engine evidence only; do not claim SDK recovery was demonstrated.'},'latest_engineering_recovery_review':read('architecture-recovery/review.json'),'current_engineering_verification':read('continuation114-recovery-verification.json'),
      'authorization':{'historical_explicit_grants':histories,'latest_full_explicit_grant':read('authorization-extension-114.json'),'charged_before_this_review':charges,'statuses':statuses,'all_original_88_operation_rows_unchanged':old_ops==current,'no_counter_reset':True,'STOP':False,'external_business_operations':0,'business_Coder_calls':0},
      'limitations':['One complete held-out case supports bounded planning evidence, not universal reliability','Eight original failures remain FAIL; engineering corrections must not be called autonomous Pello self-repair','Proposed criteria are not generated, protected or executed product tests','No business integrations or external operations; no full product delivery or Phase3D'],
      'grading_source':grading}
    evidence={'objective':'Final independent Phase3C closure against original objectives, complete frozen held-out evidence, all objective gates, relevant diff, regression and historical integrity. PASS only if every mandatory condition is verified.',
      'changed_files':code['manifest']['changed_files']+['frozen ParcelProof evaluation and local evidence harnesses'],
      'diff':json.dumps(packet,ensure_ascii=False,separators=(',',':')),
      'test_command':'Full unittest, six protected suites, source/SQLite/checkpoint/authorization/restart gates',
      'test_exit_code':0,'tests_run':reg['tests_run'],'tests_passed':reg['tests_run'],'tests_failed':0,
      'scope_constraints':[{'plan_sha256':recovered['plan_sha256'],'regression':reg,'protected_suites_intact':True},'Planning-only; no Phase3D; frozen rubric and mandatory objective gates cannot be changed']}
    canonical=json.dumps(evidence,ensure_ascii=False,separators=(',',':'))
    (out/'final-i-review-complete-input.json').write_text(canonical,encoding='utf-8')
    if len(json.dumps(evidence,ensure_ascii=False))>48000:
        # Send a deterministic prefix, then the exact remainder in the verdict
        # request. Both carry one complete-input identity in the SAME session.
        split=16000
        while True:
            part={'objective':'Receive the ordered prefix of the complete final independent closure evidence JSON. Retain it in this SAME Reviewer session. No verdict until the following request supplies the exact remainder and grading instruction.','complete_input_sha256':hashlib.sha256(canonical.encode()).hexdigest(),'complete_characters':len(canonical),'start':0,'data_json_part':canonical[:split]}
            final={**evidence,'diff':'The complete independent closure input is the concatenation of the prefix in your immediately previous receipt turn and this exact remainder. Parse and evaluate that complete original evidence JSON together with the prior original-source semantic and full diff reviews in this SAME session. No facts were omitted. Complete-input SHA256='+hashlib.sha256(canonical.encode()).hexdigest()+'\nREMAINDER START='+str(split)+'\n'+canonical[split:]}
            if len(json.dumps(final,ensure_ascii=False))<=48000:break
            split+=2000
        assert len(core._prompt('final-i-closure-prefix',part))<=45000
        assert part['data_json_part']+canonical[split:]==canonical
        (out/'final-i-review-prefix.json').write_text(json.dumps(part,ensure_ascii=False,indent=2),encoding='utf-8')
        ack,raw=core._invoke(rid,1,'final-i-closure-prefix','reviewer',part,ClosureReceipt)
        assert raw['thread_id']==evaluation['review_thread_id']
        evidence=final
    assert len(json.dumps(evidence,ensure_ascii=False))<=50000
    (out/'final-i-review-input.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    review=core.review_engineering_increment(rid,'3c3-final-heldout-i',evidence=evidence)
    (out/'final-i-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8');print(json.dumps(review,indent=2),flush=True)
    assert review['verdict']=='PASS'
    accepted=core.approve_plan(pid,review_project_id=rid,review_phase='engineering-review-3c3-final-heldout-i')
    inspection=core.inspect_plan(pid)
    assert accepted['approval']=='ACCEPTED' and inspection['execution_authorized'] is False
    (out/'accepted-i-plan-checkpoint.json').write_text(json.dumps({'accepted':accepted,'inspection':inspection,'at':datetime.now(timezone.utc).isoformat(),'review':review},indent=2),encoding='utf-8')
finally:core.backend.close()
