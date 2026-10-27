"""Register objective/semantic gates and preparation before first Planner inference."""
import hashlib,json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3')
accepted=json.loads((out/'heldout-i-preparation-accepted.json').read_text())
assert accepted['status']=='ACCEPTED'
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3')
n=c.execute('select count(*) from pello_product_projects where project_id=?',('phase3c3-heldout-i',)).fetchone()[0]
assert n==0
reg={'registered_at':datetime.now(timezone.utc).isoformat(),'planner_project_rows':n,
     'objective_script_sha256':hashlib.sha256((out/'objective_checks_i.py').read_bytes()).hexdigest(),
     'criteria_source':'heldout-i-freeze.json; private rubric unchanged',
     'critical_gate':'All structural checks, all critical semantic criteria, >=90% total; no Reviewer override',
     'eight_prior_original_FAILs_preserved':True}
(out/'objective-registration-i.json').write_text(json.dumps(reg,indent=2),encoding='utf-8')
files=['heldout-i-spec.md','heldout-i-freeze.json','heldout-i-preparation-accepted.json','heldout-i-preparation-review-complete.json','objective_checks_i.py','objective-registration-i.json','review_semantics_i.py','pack_review.py','evaluation_models.py','full-boundary-i-objective.json','rubric-i-alias-proof.json']
checkpoint={'status':'ACCEPTED','at':datetime.now(timezone.utc).isoformat(),'evaluation':'phase3c3-heldout-i-v1',
            'hashes':{p:hashlib.sha256((out/p).read_bytes()).hexdigest() for p in files},
            'eight_prior_FAILs_preserved':True,'private_expected_solution_not_sent_to_Planner_or_added_to_Git':True}
(out/'batch1-i-checkpoint.json').write_text(json.dumps(checkpoint,indent=2),encoding='utf-8')
print(json.dumps({'status':'ACCEPTED','registered_hashes':len(files),'no_planner_yet':True},indent=2))
c.close()
