"""Tooling preparation only; no fixture or SDK call before explicit95 grant."""
from pathlib import Path
out=Path('evidence/phase3c3');assert not (out/'prepare_fresh_g.py').exists()
names=['verify_full_boundary','review_preparation','run_planning','objective_checks','review_semantics','run_regression','checkpoint_preparation','review_final_code','final_review','build_success_reports']
for name in names+['verify_rubric']:
 old='verify_rubric_f_paths.py' if name=='verify_rubric' else name+'_f.py'
 new='verify_rubric_g_paths.py' if name=='verify_rubric' else name+'_g.py'
 s=(out/old).read_text(encoding='utf-8')
 for a,b in [('heldout-f','heldout-g'),('phase3c3-review-f','phase3c3-review-g'),('boundary-f','boundary-g'),('rubric-f','rubric-g'),('registration-f','registration-g'),('batch1-f','batch1-g'),('checks_f.py','checks_g.py'),('semantics_f.py','semantics_g.py')]:s=s.replace(a,b)
 s=s.replace('count>=240','count>=245').replace("reg['tests_run']>=240","reg['tests_run']>=245")
 s=s.replace("out/'planning-context-correction/protection.json']","out/'planning-context-correction/protection.json',out/'contract-context-correction/protection.json']")
 if name in ['final_review','review_final_code']:
  s=s.replace("'planning-context-correction']","'planning-context-correction','contract-context-correction']")
  s=s.replace("'heldout-e-evaluation.json']","'heldout-e-evaluation.json','heldout-f-evaluation.json']")
  s=s.replace('charges<85','charges<95').replace('authorization-extension-85.json','authorization-extension-95.json')
  s=s.replace('Five initial','Six initial').replace('five original','six original').replace('seven-test-source','eight-test-source').replace('seven protected','eight protected').replace('3c3-final-code-f','3c3-final-code-g')
 if name=='checkpoint_preparation':s=s.replace('five_prior','six_prior').replace('A_B_C_D_E_FAILs','A_B_C_D_E_F_FAILs')
 if name=='build_success_reports':
  s=s.replace("'f':fresh_name","'f':'AssemblyCount','g':fresh_name").replace('Five earlier','Six earlier').replace('five earlier','six earlier').replace('five retained','six retained').replace('four retained','six retained').replace('Twenty-three new protected','Twenty-eight new protected')
 (out/new).write_text(s,encoding='utf-8')
s=(out/'prepare_fresh_f.py').read_text(encoding='utf-8')
s=s.replace('heldout-f','heldout-g').replace('phase3c3-review-f','phase3c3-review-g').replace("/'phase3c3-f'","/'phase3c3-g'").replace('heldout-e-freeze.json','heldout-f-freeze.json')
s=s.replace('planning-context-correction/review.json','contract-context-correction/review.json').replace('authorization-extension-85.json','authorization-extension-95.json').replace('==85','==95')
s=s.replace('StackProof air-permit emissions compliance,','StackProof air-permit emissions compliance, AssemblyCount cooperative meeting credentials and voting,').replace('All five prior','All six prior')
(out/'prepare_fresh_g.py').write_text(s,encoding='utf-8')
print('Prepared G tooling; no new business source, expected solution or SDK call created.')
