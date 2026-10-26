"""Record explicit85 cumulative grant; preserve every operation and counter."""
import json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');deadline='2026-10-26T06:30:00+00:00';identifier='phase3c3-extension-85-20261026'
assert datetime.now(timezone.utc)<datetime.fromisoformat(deadline)
assert not Path('runtime/phase3c/STOP').exists()
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
with c:
 c.execute('BEGIN IMMEDIATE')
 assert c.execute('select count(*) from pello_product_operations').fetchone()[0]==62
 assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]==62
 previous=dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone())
 assert previous['max_turns']==75 and previous['deadline']==deadline
 author=dict(c.execute("select * from pello_product_projects where project_id='phase3c3-author'").fetchone())
 (out/'before-extension-85-author.json').write_text(json.dumps(author,indent=2))
 grant={'id':identifier,'authorized_at':datetime.now(timezone.utc).isoformat(),'user_authorization':'Autorizo 85 acumulados y mantengo ese plazo','authorization_source':'Explicit reply to85 cumulative / same2026-10-26 06:30 UTC question','cumulative_sdk_limit':85,'deadline':deadline,'already_reserved':62,'completed_calls':60,'terminal_provider_failure_retained':1,'never_submitted_charge_retained':1,'remaining_slots':23,'no_counter_reset':True,'external_business_operations':0,'per_project_limit':12,'scope':'Phase3C-3 fresh independent held-out evaluation, justified localized correction if needed, bounded independent semantic and final reviews, regression/checkpoint. No Phase3D.','allocation':{'fresh_specification_planning_bounded_reviews':14,'failure_reserve':9},'prior_authorization':previous['id'],'renew_author_deadline_only':{'old_deadline':author['deadline'],'new_deadline':deadline,'used_turns_unchanged':author['used_turns']}}
 (out/'authorization-extension-85.json').write_text(json.dumps(grant,indent=2))
 c.execute('insert into pello_product_run_authorizations values(?,?,?,?)',(identifier,json.dumps(grant),deadline,85))
 c.execute("update pello_product_projects set deadline=? where project_id='phase3c3-author'",(deadline,))
 assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]==62
print(json.dumps(grant,indent=2));c.close()
