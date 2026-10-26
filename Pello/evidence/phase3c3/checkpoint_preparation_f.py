import hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3')
assert json.loads((out/'heldout-f-preparation-accepted.json').read_text())['status']=='ACCEPTED'
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3')
n=c.execute('select count(*) from pello_product_projects where project_id=?',('phase3c3-heldout-f',)).fetchone()[0]
assert n==0
reg={'registered_at':datetime.now(timezone.utc).isoformat(),'planner_project_rows':n,
     'objective_script_sha256':hashlib.sha256((out/'objective_checks_f.py').read_bytes()).hexdigest(),
     'criteria_source':'heldout-f-freeze.json; frozen hidden rubric unchanged',
     'critical_gate':'All structural checks, all critical semantic criteria, and >=90% total pass; no Reviewer override',
     'previous_A_B_C_D_E_FAILs_preserved':True}
(out/'objective-registration-f.json').write_text(json.dumps(reg,indent=2))
files=['heldout-f-spec.md','heldout-f-freeze.json','heldout-f-preparation-accepted.json','heldout-f-preparation-review-complete.json','objective_checks_f.py','objective-registration-f.json','review_semantics_f.py']
checkpoint={'status':'ACCEPTED','at':datetime.now(timezone.utc).isoformat(),'evaluation':'phase3c3-heldout-f-v1',
            'hashes':{p:hashlib.sha256((out/p).read_bytes()).hexdigest() for p in files},
            'five_prior_FAILs_preserved':True,'new_expected_solution_not_sent_to_Planner_or_added_to_Git':True}
(out/'batch1-f-checkpoint.json').write_text(json.dumps(checkpoint,indent=2));print(json.dumps(checkpoint,indent=2))
c.close()
