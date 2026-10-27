"""Inspect actual submitted contexts and permission receipts, never infer blindness."""
import hashlib,json,sqlite3
from pathlib import Path
out=Path('evidence/phase3c3');freeze=json.loads((out/'heldout-i-freeze.json').read_text())
folder=Path('runtime/phase3c/projects/phase3c3-heldout-i')
checks=[]
for path in sorted((folder/'evidence').glob('version-1/*/model-turn-submitted.json')):
    receipt=json.loads(path.read_text());isolation=receipt['context_isolation']
    profile=receipt['active_permission_profile']
    inp=path.with_name('input.json').read_text()
    denied=isolation['permissions.pello_supplied_context']['filesystem']
    checks.append({'phase':path.parent.name,'thread_id':receipt['thread_id'],'role':receipt['role'],
        'profile_valid':profile['id']=='pello_supplied_context' and profile['extends']==':read-only',
        'network_disabled':not isolation['permissions.pello_supplied_context']['network']['enabled'],
        'reading_and_external_surfaces_disabled':all(isolation.get('features.'+name) is False for name in ['shell_tool','unified_exec','view_image','code_mode','code_mode_host','browser_use','computer_use','in_app_browser','apps','plugins','multi_agent','multi_agent_v2','memories','skill_search']),
        'automatic_project_docs_disabled':isolation['project_doc_max_bytes']==0,
        'all_frozen_roots_denied':all(denied.get(Path(root).as_posix())=='deny' for root in freeze['deny_read_roots']),
        'no_evaluator_key_fields_in_context':all(name not in inp for name in ['expected_planning_outcome','minimum_critical_pass_fraction','frozen_rubric','private_rubric_path']),
        'input_file_sha256':hashlib.sha256(path.with_name('input.json').read_bytes()).hexdigest(),
        'receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
conn=sqlite3.connect(Path('runtime/phase3c/jobs.sqlite3').resolve().as_uri()+'?mode=ro',uri=True);conn.row_factory=sqlite3.Row
sessions=[dict(x) for x in conn.execute("select project_id,role,thread_id from pello_sessions where project_id in ('phase3c3-author','phase3c3-heldout-i','phase3c3-review-i')")]
planner={x['thread_id'] for x in sessions if x['project_id']=='phase3c3-heldout-i'}
others={x['thread_id'] for x in sessions if x['project_id']!='phase3c3-heldout-i'}
valid=bool(checks) and all(all(v for k,v in row.items() if k.endswith(('_valid','_disabled','_denied','_context'))) for row in checks) and not planner&others
result={'verdict':'PASS' if valid else 'FAIL','submitted_contexts':checks,'sessions':sessions,'author_and_evaluation_reviewer_separate_from_Pello_roles':not bool(planner&others),'private_key_unchanged':hashlib.sha256(Path(freeze['private_rubric_path']).read_bytes()).hexdigest()==freeze['rubric_sha256'],'private_key_fields_not_supplied':all(x['no_evaluator_key_fields_in_context'] for x in checks)}
assert result['private_key_unchanged']
(out/'heldout-i-actual-isolation-audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'verdict':result['verdict'],'submitted_contexts':len(checks),'separate_sessions':result['author_and_evaluation_reviewer_separate_from_Pello_roles']},indent=2));assert valid
