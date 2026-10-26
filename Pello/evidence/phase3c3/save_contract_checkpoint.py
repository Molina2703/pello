"""Final correction checkpoint after user declined further SDK capacity."""
import ast,hashlib,json,sqlite3,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');d=out/'contract-context-correction'
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
reg=read('contract-regression.json');integrity=read('contract-integrity.json');protected=read('contract-protected.json');review=read('contract-context-correction/review.json')
assert reg['exit_code']==0 and reg['tests_run']==245 and integrity['historical_hashes_matching']==1493
assert all(p['exit_code']==0 and p['source_hashes_intact'] and p['protected_copy_hash_intact'] for p in protected)
assert integrity['first_28_sdk_operation_rows_unchanged'] and integrity['original_projects_preserved'] and review['verdict']=='PASS'
baseline=subprocess.check_output(['git','show','c1bb076e7059100f0c4b5abf623625d2843f0be2:Pello/athis_autopilot/planning_contracts.py'],text=True,encoding='utf-8')
current=Path('athis_autopilot/planning_contracts.py').read_text(encoding='utf-8')
def functions(s):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
a,b=functions(baseline),functions(current)
validators={name:a[name]==b[name] for name in ['validate_architecture','validate_increments','validate_contracts','manifest_from_contracts']};assert all(validators.values())
proof=read('contract-context-correction/objective-proof.json');f=read('heldout-f-freeze.json')
assert proof['batches']['source_sha256']==f['specification_sha256']
accepted={'status':'ACCEPTED_CORRECTION_ONLY','regression':reg,'protected_tests':sum(p['tests_run'] for p in protected),'historical_hashes':1493,'review':review,'validators_ast_identical_to_accepted_C2':validators,'source_identity_verified':True,'six_original_blind_FAILs_preserved':True,'blind_generalization':'UNVERIFIED','fresh_case_required':True,'user_decision':'Conservar el checkpoint sin ampliar','no_further_SDK_authorized_by_this_checkpoint':True}
(d/'accepted-regression-checkpoint.json').write_text(json.dumps(accepted,indent=2),encoding='utf-8')
decision={'at':datetime.now(timezone.utc).isoformat(),'user_reply':'Conservar el checkpoint sin ampliar','question_proposed_limit':95,'question_proposed_deadline':'2026-10-26T06:30:00+00:00','decision':'PRESERVE_CHECKPOINT_NO_BUDGET_INCREASE_NO_FURTHER_SDK','cumulative_limit_unchanged':85,'counters_not_reset':True,'new_heldout_G_not_started':True}
(out/'user-decision-preserve-checkpoint-69.json').write_text(json.dumps(decision,indent=2),encoding='utf-8')
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
count=c.execute('select count(*) from pello_product_operations').fetchone()[0];assert count==69
assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]==69
statuses=[dict(r) for r in c.execute('select status,count(*) as count from pello_product_operations group by status')]
assert {s['status'] for s in statuses}<={'COMPLETED','FAILED_PROVIDER_QUOTA_RECONCILED','NOT_SUBMITTED_CONTEXT_REJECTED'}
auth=dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone());assert auth['max_turns']==85
assert c.execute("select count(*) from pello_product_projects where project_id='phase3c3-heldout-g'").fetchone()[0]==0
backup_path=out/'checkpoint-69-jobs.sqlite3';backup=sqlite3.connect(backup_path);c.backup(backup);backup.close()
checkpoints=[dict(r) for r in c.execute('select * from pello_product_checkpoints order by rowid')]
for cp in checkpoints:
 folder=Path('runtime/phase3c/projects')/cp['project_id']/'workspace'
 assert subprocess.run(['git','-C',str(folder),'cat-file','-e',cp['commit_sha']+'^{commit}'],capture_output=True).returncode==0
state={'at':datetime.now(timezone.utc).isoformat(),'status':'PARTIAL','execution_decision':decision['decision'],'cumulative_limit':85,'deadline':auth['deadline'],'charged_reservations':69,'remaining_unspent_slots':16,'statuses':statuses,'STOP':Path('runtime/phase3c/STOP').exists(),'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],'checkpoint_count':len(checkpoints),'all_checkpoint_git_objects_verified':True,'regression_tests':245,'protected_tests':63,'historical_hashes':1493,'source_and_validator_proof':accepted,'six_original_blind_FAILs_preserved':True,'new_G_fixture_and_Planner_not_created':True,'external_business_operations':0,'Phase3D_started':False,'snapshot_sha256':hashlib.sha256(backup_path.read_bytes()).hexdigest()}
assert not state['STOP'] and state['sqlite_integrity']=='ok'
(out/'checkpoint-69-state.json').write_text(json.dumps(state,indent=2),encoding='utf-8');c.close()
print(json.dumps({k:v for k,v in state.items() if k!='source_and_validator_proof'},indent=2))
