"""Record the user's explicit renewed authorization, without resetting consumption."""
import json,sqlite3
from datetime import datetime,timezone
from pathlib import Path

out=Path('evidence/phase3c3')
with sqlite3.connect('runtime/phase3c/jobs.sqlite3') as c:
    c.row_factory=sqlite3.Row
    c.execute('BEGIN IMMEDIATE')
    assert not (out/'authorization-extension-101.json').exists()
    previous=dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone())
    assert previous['max_turns']==95
    count=c.execute('select count(*) from pello_product_operations').fetchone()[0]
    assert count==75==c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]
    assert not Path('runtime/phase3c/STOP').exists()
    author=dict(c.execute("select * from pello_product_projects where project_id='phase3c3-author'").fetchone())
    grant={'id':'phase3c3-extension-101-20261026','authorized_at':datetime.now(timezone.utc).isoformat(),
        'user_authorization':'Autorizo 101 acumulados y ese plazo',
        'authorization_source':'Explicit user reply to cumulative101 / October27 06:30 UTC request in this chat',
        'cumulative_sdk_limit':101,'deadline':'2026-10-27T06:30:00+00:00',
        'already_reserved':count,'completed_calls':73,'terminal_provider_failure_retained':1,
        'never_submitted_charge_retained':1,'remaining_slots':26,'no_counter_reset':True,
        'external_business_operations':0,'per_project_limit':12,
        'scope':'One fresh Phase3C-3 blind evaluation, bounded actual planning and independent semantic/final reviews; justified localized correction and regression if needed; no Phase3D.',
        'allocation':{'complete_fresh_evaluation_and_reviews':20,'failure_reserve':6},
        'prior_authorization':previous['id'],
        'supersedes_preservation_decision_for_new_authorized_scope_only':True,
        'renew_author_deadline_only':{'old_deadline':author['deadline'],'new_deadline':'2026-10-27T06:30:00+00:00','used_turns_unchanged':author['used_turns']}}
    assert datetime.now(timezone.utc)<datetime.fromisoformat(grant['deadline'])
    encoded=json.dumps(grant,ensure_ascii=False)
    c.execute('insert into pello_product_run_authorizations values(?,?,?,?)',(grant['id'],encoded,grant['deadline'],101))
    c.execute("update pello_product_projects set deadline=? where project_id='phase3c3-author'",(grant['deadline'],))
    (out/'authorization-extension-101.json').write_text(json.dumps(grant,indent=2)+'\n',encoding='utf-8')
print(json.dumps(grant,indent=2))
