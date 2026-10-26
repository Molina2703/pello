import hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3')
assert json.loads((out/'heldout-h-preparation-accepted-v2.json').read_text())['status']=='ACCEPTED'
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3')
n=c.execute('select count(*) from pello_product_projects where project_id=?',('phase3c3-heldout-h',)).fetchone()[0]
assert n==0
reg={'registered_at':datetime.now(timezone.utc).isoformat(),'planner_project_rows':n,
     'objective_script_sha256':hashlib.sha256((out/'objective_checks_h.py').read_bytes()).hexdigest(),
     'criteria_source':'heldout-h-freeze-v2.json; frozen hidden rubric unchanged',
     'critical_gate':'All structural checks, all critical semantic criteria, and >=90% total pass; no Reviewer override',
     'previous_A_B_C_D_E_F_G_FAILs_preserved':True}
(out/'objective-registration-h.json').write_text(json.dumps(reg,indent=2))
files=['heldout-h-spec-v2.md','heldout-h-freeze-v2.json','heldout-h-preparation-accepted-v2.json','heldout-h-preparation-review-v2-complete.json','objective_checks_h.py','objective-registration-h.json','review_semantics_h.py','pack_review.py','evaluation_models.py']
checkpoint={'status':'ACCEPTED','at':datetime.now(timezone.utc).isoformat(),'evaluation':'phase3c3-heldout-h-v1',
            'hashes':{p:hashlib.sha256((out/p).read_bytes()).hexdigest() for p in files},
            'seven_prior_FAILs_preserved':True,'new_expected_solution_not_sent_to_Planner_or_added_to_Git':True}
(out/'batch1-h-checkpoint.json').write_text(json.dumps(checkpoint,indent=2));print(json.dumps(checkpoint,indent=2))
c.close()
