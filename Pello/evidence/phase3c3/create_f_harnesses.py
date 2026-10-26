"""Prepare evaluation tooling only; does not author a fixture or submit SDK."""
from pathlib import Path
out=Path('evidence/phase3c3')
assert not (out/'prepare_fresh_f.py').exists(),'One-time bootstrap; never overwrite later frozen or corrected evaluation tooling'
names=['verify_full_boundary','verify_rubric','review_preparation','run_planning','objective_checks','review_semantics','run_regression','checkpoint_preparation','review_final_code','final_review','build_success_reports']
for name in names:
    source_name=('verify_rubric_e_paths.py' if name=='verify_rubric' else name+'_e.py')
    target_name=('verify_rubric_f_paths.py' if name=='verify_rubric' else name+'_f.py')
    text=(out/source_name).read_text(encoding='utf-8')
    for old,new in [('heldout-e','heldout-f'),('phase3c3-review-e','phase3c3-review-f'),('boundary-e','boundary-f'),('rubric-e','rubric-f'),('registration-e','registration-f'),('batch1-e','batch1-f'),('checks_e.py','checks_f.py'),('semantics_e.py','semantics_f.py'),('2026-10-26T03:30:00+00:00','2026-10-26T06:30:00+00:00')]:text=text.replace(old,new)
    text=text.replace('count>=236','count>=240').replace("out/'architecture-contract-correction/protection.json']","out/'architecture-contract-correction/protection.json',out/'planning-context-correction/protection.json']")
    if name in ['review_final_code','final_review']:
        text=text.replace("'architecture-contract-correction']","'architecture-contract-correction','planning-context-correction']")
        text=text.replace("'heldout-d-evaluation.json']","'heldout-d-evaluation.json','heldout-e-evaluation.json']")
        text=text.replace('four original','five original').replace('Four original','Five original')
    if name=='final_review':
        text=text.replace('charges<75','charges<85').replace("read('authorization-deadline-0630.json')","read('authorization-extension-85.json')")
    if name=='checkpoint_preparation':
        text=text.replace('A_B_C_D_FAILs','A_B_C_D_E_FAILs').replace('four_prior','five_prior')
    if name=='build_success_reports':
        text=text.replace("'e':'StackProof'","'e':'StackProof','f':'NEW_CASE'").replace('Four earlier','Five earlier').replace('four retained','five retained').replace('Four initial','Five initial').replace('four initial','five initial').replace('Four original','Five original').replace('four original','five original').replace('four earlier','five earlier').replace('Nineteen new protected','Twenty-three new protected').replace('six-test-source','seven-test-source')
    (out/target_name).write_text(text,encoding='utf-8')
text=(out/'prepare_fresh_e.py').read_text(encoding='utf-8')
text=text.replace('architecture-contract-correction/review.json','planning-context-correction/review.json').replace('heldout-d-freeze.json','heldout-e-freeze.json').replace("/'phase3c3-e'","/'phase3c3-f'").replace('phase3c3-review-e','phase3c3-review-f').replace('heldout-e','heldout-f').replace('FolioPay royalty settlement and payments,','FolioPay royalty settlement and payments, StackProof air-permit emissions compliance,').replace('All four prior','All five prior')
text=text.replace("out=Path('evidence/phase3c3');assert", "out=Path('evidence/phase3c3');assert json.loads((out/'authorization-extension-85.json').read_text())['cumulative_sdk_limit']==85\nassert")
(out/'prepare_fresh_f.py').write_text(text,encoding='utf-8')
print('Prepared fresh-F tooling; no fixture, hidden expectations or SDK request created.')
