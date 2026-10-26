"""Append the user's explicit deadline-only grant; preserve all consumption."""
import json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');deadline='2026-10-26T06:30:00+00:00';identifier='phase3c3-deadline-0630-20261026'
assert datetime.now(timezone.utc)<datetime.fromisoformat(deadline)
assert not Path('runtime/phase3c/STOP').exists()
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
with c:
 c.execute('BEGIN IMMEDIATE')
 assert c.execute('select count(*) from pello_product_operations').fetchone()[0]==60
 assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]==60
 assert c.execute('select count(*) from pello_product_run_authorizations where id=?',(identifier,)).fetchone()[0]==0
 previous=dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone())
 assert previous['max_turns']==75 and previous['deadline']=='2026-10-26T03:30:00+00:00'
 rows=[dict(c.execute('select * from pello_product_projects where project_id=?',(p,)).fetchone()) for p in ['phase3c3-heldout-e','phase3c3-review-e']]
 grant={'id':identifier,'authorized_at':datetime.now(timezone.utc).isoformat(),'user_authorization':'Autorizo ese plazo y mantengo 75 acumulados',
  'authorization_source':'Explicit reply to deadline-only extension question: 2026-10-26 06:30 UTC / 01:30 Colombia; maximum remains75',
  'deadline':deadline,'cumulative_sdk_limit':75,'already_reserved':60,'completed_calls':58,'terminal_provider_failures_retained':1,'never_submitted_charge_retained':1,
  'remaining_slots':15,'external_business_operations':0,'per_project_limit':12,'no_counter_reset':True,
  'scope':'Complete current Phase 3C-3 independent planning evaluation, objective/semantic review, regression and independent final review if justified; no Phase 3D',
  'prior_authorization':previous['id'],'renew_existing_project_deadlines_only':[{'project_id':r['project_id'],'old_deadline':r['deadline'],'new_deadline':deadline,'used_turns_unchanged':r['used_turns']} for r in rows]}
 (out/'before-deadline-0630-projects.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 (out/'authorization-deadline-0630.json').write_text(json.dumps(grant,indent=2),encoding='utf-8')
 c.execute('insert into pello_product_run_authorizations values(?,?,?,?)',(identifier,json.dumps(grant),deadline,75))
 for r in rows:c.execute('update pello_product_projects set deadline=? where project_id=?',(deadline,r['project_id']))
 assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]==60
print(json.dumps(grant,indent=2));c.close()
