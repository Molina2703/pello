"""Append the explicit bounded continuation; preserve all charged reservations."""
import json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

out = Path('evidence/phase3c3')
with sqlite3.connect('runtime/phase3c/jobs.sqlite3') as c:
    c.row_factory = sqlite3.Row
    c.execute('BEGIN IMMEDIATE')
    assert not (out/'authorization-extension-114.json').exists()
    previous = dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone())
    count = c.execute('select count(*) from pello_product_operations').fetchone()[0]
    author = dict(c.execute("select * from pello_product_projects where project_id='phase3c3-author'").fetchone())
    assert previous['max_turns'] == 101 and count == 88
    assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0] == count
    assert (author['used_turns'], author['max_turns']) == (14, 14)
    assert not Path('runtime/phase3c/STOP').exists()
    grant = {
        'id': 'phase3c3-extension-114-author18-20261027',
        'authorized_at': datetime.now(timezone.utc).isoformat(),
        'user_authorization': 'Autorizo 114 globales, autor 18 y ese plazo',
        'authorization_source': 'Explicit user reply to the 114 global / author18 / October27 06:30 UTC question in this chat',
        'cumulative_sdk_limit': 114, 'already_reserved': count,
        'deadline': '2026-10-27T06:30:00+00:00',
        'author_project_id': 'phase3c3-author', 'author_used_unchanged': 14,
        'old_author_max_turns': 14, 'approved_author_max_turns': 18,
        'remaining_global_slots': 26,
        'allocation': {'one_fresh_case_complete_planning_and_reviews': 20, 'failure_reserve': 6},
        'author_four_slots_included_in_global': True,
        'other_project_limits_unchanged': 12,
        'scope': 'One fresh blind Phase3C-3 evaluation through complete planning, independent semantic/final reviews, justified localized correction and regression. No Phase3D or business-product Coder execution.',
        'supersedes_preservation_decision_for_this_scope': True,
        'external_business_operations': 0, 'no_counter_reset': True,
        'prior_authorization': previous['id'],
    }
    assert datetime.now(timezone.utc) < datetime.fromisoformat(grant['deadline'])
    c.execute('insert into pello_product_run_authorizations values(?,?,?,?)',
              (grant['id'], json.dumps(grant, ensure_ascii=False), grant['deadline'], 114))
    c.execute("update pello_product_projects set max_turns=18, deadline=? where project_id='phase3c3-author'",
              (grant['deadline'],))
    (out/'authorization-extension-114.json').write_text(json.dumps(grant, indent=2)+'\n', encoding='utf-8')
print(json.dumps(grant, indent=2))
