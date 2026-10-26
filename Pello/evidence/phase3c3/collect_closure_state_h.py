"""Read-only reconciliation plus a SQLite backup; no accounting mutation."""
import hashlib,json,sqlite3,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');db=Path('runtime/phase3c/jobs.sqlite3')
c=sqlite3.connect(db);c.row_factory=sqlite3.Row
operations=[dict(x) for x in c.execute('select * from pello_product_operations order by rowid')]
statuses={}
for op in operations:statuses[op['status']]=statuses.get(op['status'],0)+1
assert not any(k not in {'COMPLETED','NOT_SUBMITTED_CONTEXT_REJECTED','FAILED_PROVIDER_QUOTA_RECONCILED','NOT_SUBMITTED_ACTIVE_WRITER_RECONCILED'} for k in statuses),statuses
authorizations=[dict(x) for x in c.execute('select * from pello_product_run_authorizations order by rowid')]
assert len(operations)<=authorizations[-1]['max_turns'] and datetime.now(timezone.utc)<datetime.fromisoformat(authorizations[-1]['deadline'])
checkpoints=[dict(x) for x in c.execute('select * from pello_product_checkpoints order by rowid')]
for checkpoint in checkpoints:
 workspace=Path('runtime/phase3c/projects')/checkpoint['project_id']/'workspace'
 assert subprocess.run(['git','-C',str(workspace),'cat-file','-e',checkpoint['commit_sha']+'^{commit}'],capture_output=True).returncode==0
projects=[dict(x) for x in c.execute('select * from pello_product_projects order by rowid')]
dest=out/'closure-jobs.sqlite3';backup=sqlite3.connect(dest);c.backup(backup);backup.close()
summary={'at':datetime.now(timezone.utc).isoformat(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
 'stop_set':Path('runtime/phase3c/STOP').exists(),'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],
 'sdk_charged_reservations':len(operations),'actual_completed_sdk_calls':statuses.get('COMPLETED',0),
 'never_submitted_retained_charge':statuses.get('NOT_SUBMITTED_CONTEXT_REJECTED',0),'provider_failed_retained_charge':statuses.get('FAILED_PROVIDER_QUOTA_RECONCILED',0),'writer_rejected_retained_charge':statuses.get('NOT_SUBMITTED_ACTIVE_WRITER_RECONCILED',0),'remaining_authorized_slots':authorizations[-1]['max_turns']-len(operations),
 'authorization_rows':authorizations,'deadline':authorizations[-1]['deadline'],'cumulative_limit':authorizations[-1]['max_turns'],
 'statuses':statuses,'projects':projects,'checkpoints':checkpoints,'all_checkpoint_git_objects_verified_after_acceptance':True,'external_business_operations':0,'Phase3D_started':False,
 'snapshot_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
(out/'closure-state.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k not in {'projects','checkpoints','authorization_rows'}},indent=2))
c.close()
