import hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3')
assert json.loads((out/'heldout-g-preparation-accepted-v2.json').read_text())['status']=='ACCEPTED'
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3')
n=c.execute('select count(*) from pello_product_projects where project_id=?',('phase3c3-heldout-g',)).fetchone()[0]
assert n==0
reg={'registered_at':datetime.now(timezone.utc).isoformat(),'planner_project_rows':n,
     'objective_script_sha256':hashlib.sha256((out/'objective_checks_g.py').read_bytes()).hexdigest(),
     'criteria_source':'heldout-g-freeze-v2.json; frozen hidden rubric unchanged',
     'critical_gate':'All structural checks, all critical semantic criteria, and >=90% total pass; no Reviewer override',
     'previous_A_B_C_D_E_F_FAILs_preserved':True}
(out/'objective-registration-g.json').write_text(json.dumps(reg,indent=2))
files=['heldout-g-spec.md','heldout-g-freeze-v2.json','heldout-g-preparation-accepted-v2.json','heldout-g-preparation-review-v2-complete.json','objective_checks_g.py','objective-registration-g.json','review_semantics_g.py','pack_review.py','evaluation_models.py']
checkpoint={'status':'ACCEPTED','at':datetime.now(timezone.utc).isoformat(),'evaluation':'phase3c3-heldout-g-v1',
            'hashes':{p:hashlib.sha256((out/p).read_bytes()).hexdigest() for p in files},
            'six_prior_FAILs_preserved':True,'new_expected_solution_not_sent_to_Planner_or_added_to_Git':True}
(out/'batch1-g-checkpoint.json').write_text(json.dumps(checkpoint,indent=2));print(json.dumps(checkpoint,indent=2))
c.close()
