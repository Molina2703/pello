"""Accept only the verified engineering correction, retaining the seventh blind FAIL."""
import hashlib,json,sqlite3,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');d=out/'analysis-transport-correction'
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
reg=read('analysis-transport-regression.json');integrity=read('analysis-transport-integrity.json');protected=read('analysis-transport-protected.json');review=read('analysis-transport-correction/review.json')
assert reg['exit_code']==0 and reg['tests_run']==249 and review['verdict']=='PASS'
assert integrity['historical_hashes_matching']==1493 and not integrity['mismatches']
assert integrity['first_28_sdk_operation_rows_unchanged'] and integrity['original_projects_preserved']
assert integrity['sqlite_integrity']=='ok' and all(p['commit_present'] for p in integrity['checkpoint_commits'])
assert all(p['matches'] for p in integrity['new_protected_test_sources']) and integrity['frozen_objective_script_intact']
assert all(p['exit_code']==0 and p['source_hashes_intact'] and p['protected_copy_hash_intact'] for p in protected)
assert sum(p['tests_run'] for p in protected)==63
pr=read('analysis-transport-correction/protection.json')
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pr['hashes'].items())
assert hashlib.sha256((d/'original-review-input.json').read_bytes()).hexdigest()==pr['fixture_sha256']
for letter in 'abcdefg':assert read(f'heldout-{letter}-evaluation.json')['verdict']=='FAIL'
proof=read('analysis-transport-correction/objective-proof.json');assert all(proof['validators_unchanged'].values())
f=read('heldout-g-freeze-v2.json')
assert hashlib.sha256((out/'heldout-g-spec.md').read_bytes()).hexdigest()==f['specification_sha256']
assert hashlib.sha256(Path(f['private_rubric_path']).read_bytes()).hexdigest()==f['rubric_sha256']
accepted={'status':'ACCEPTED_CORRECTION_ONLY','at':datetime.now(timezone.utc).isoformat(),'regression':reg,'protected_C2':63,'protected_C3_defect_checks':32,'historical_hashes':1493,'review':review,'proof':proof,'source_sha256':hashlib.sha256(Path('athis_autopilot/product_planning.py').read_bytes()).hexdigest(),'seven_original_blind_FAILs_preserved':True,'blind_generalization':'UNVERIFIED','fresh_case_required':True,'no_corrected_G_SDK_rerun':True,'no_product_implementation':True,'Phase3D_started':False}
(d/'accepted-regression-checkpoint.json').write_text(json.dumps(accepted,indent=2))
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
count=c.execute('select count(*) from pello_product_operations').fetchone()[0];assert count==75==c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]
statuses=[dict(r) for r in c.execute('select status,count(*) as count from pello_product_operations group by status')]
assert {s['status'] for s in statuses}<={'COMPLETED','FAILED_PROVIDER_QUOTA_RECONCILED','NOT_SUBMITTED_CONTEXT_REJECTED'}
auth=dict(c.execute('select id,max_turns,deadline from pello_product_run_authorizations order by rowid desc limit 1').fetchone());assert auth['max_turns']==95
assert c.execute("select count(*) from pello_product_projects where project_id='phase3c3-heldout-h'").fetchone()[0]==0
backup_path=out/'checkpoint-75-jobs.sqlite3';backup=sqlite3.connect(backup_path);c.backup(backup);backup.close()
state={'at':datetime.now(timezone.utc).isoformat(),'status':'PARTIAL','overall_phase3c':'PARTIAL','cumulative_limit':95,'charged_reservations':75,'remaining_unspent_slots':20,'statuses':statuses,'deadline':auth['deadline'],'latest_authorization_id':auth['id'],'STOP':Path('runtime/phase3c/STOP').exists(),'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],'checkpoint_count':len(integrity['checkpoint_commits']),'all_checkpoint_git_objects_verified':True,'regression_tests':249,'protected_C2_tests':63,'protected_C3_tests':32,'historical_hashes':1493,'seven_original_blind_FAILs_preserved':True,'new_H_not_started':True,'no_further_SDK_after_correction_review':True,'minimum_next_route':{'complete_fresh_case_and_reviews_estimate':20,'failure_reserve':6,'required_available':26,'current_available':20,'proposed_cumulative_cap':101,'proposed_deadline_unchanged':auth['deadline'],'authorization_status':'NOT_GRANTED'},'external_business_operations':0,'Phase3D_started':False,'snapshot_sha256':hashlib.sha256(backup_path.read_bytes()).hexdigest(),'git_parent_HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
assert not state['STOP'] and state['sqlite_integrity']=='ok'
(out/'checkpoint-75-state.json').write_text(json.dumps(state,indent=2));print(json.dumps(state,indent=2));c.close()
