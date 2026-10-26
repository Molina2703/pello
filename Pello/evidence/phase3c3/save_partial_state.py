"""Record authorization-blocked checkpoint without SDK inference or acceptance."""
import hashlib,json,sqlite3,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
ops=[dict(x) for x in c.execute('select * from pello_product_operations order by rowid')]
statuses={}
for op in ops:statuses[op['status']]=statuses.get(op['status'],0)+1
assert set(statuses)<={'COMPLETED','NOT_SUBMITTED_CONTEXT_REJECTED','FAILED_PROVIDER_QUOTA_RECONCILED'}
assert len(ops)==60
auth=[dict(x) for x in c.execute('select * from pello_product_run_authorizations order by rowid')]
project=dict(c.execute('select * from pello_product_projects where project_id=?',('phase3c3-heldout-e',)).fetchone())
version=dict(c.execute('select * from pello_product_versions where project_id=?',('phase3c3-heldout-e',)).fetchone())
a=json.loads(version['analysis']);review=json.loads(version['analysis_review'])
dest=out/'checkpoint-60-jobs.sqlite3';backup=sqlite3.connect(dest);c.backup(backup);backup.close()
state={'at':datetime.now(timezone.utc).isoformat(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
 'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),'status':'PARTIAL','current_execution_gate':'AUTHORIZATION_DEADLINE_EXPIRED',
 'charged_reservations':len(ops),'statuses':statuses,'cumulative_limit':auth[-1]['max_turns'],'deadline':auth[-1]['deadline'],
 'authorization_expired':datetime.now(timezone.utc)>datetime.fromisoformat(auth[-1]['deadline']),
 'available_unused_slots':auth[-1]['max_turns']-len(ops),'authorization_rows':auth,'STOP':Path('runtime/phase3c/STOP').exists(),
 'heldout_e':{'requirements':len(a['requirements']),'issues':len(a['issues']),'assumptions':len(a['assumptions']),'segments':len(a['source_segments']),'interpretation_review':review,'complete_plan':bool(version['plan']),'project':project},
 'sdk_after_deadline':False,'new_retry_reservation':False,'counters_reset':False,'external_business_operations':0,'phase3D_started':False,
 'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],'snapshot_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
 'private_evaluation_key_still_not_published':True,'budget_needed_to_finish_current_case':{'pipeline_stages':4,'semantic_review':1,'code_and_final_reviews':2,'failure_reserve':8,'total':15}}
(out/'checkpoint-60-state.json').write_text(json.dumps(state,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in state.items() if k not in {'heldout_e','authorization_rows'}},indent=2))
c.close()
