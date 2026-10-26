"""Read-only final code review in the independent evaluation Reviewer session."""
import hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
assert read('heldout-h-evaluation.json')['verdict']=='PASS'
reg=read('final-regression.json');assert reg['exit_code']==0
diff=subprocess.check_output(['git','diff','--unified=1','c1bb076e7059100f0c4b5abf623625d2843f0be2','--','athis_autopilot','tests'],text=True,encoding='utf-8')
packet={'objective':'Independent final code review, first part of final Phase 3C closure review in this same Reviewer session. Review the complete relevant Git diff and protected defect tests for correctness, scope, SDK isolation, unchanged validators, source/context losslessness, budget and accepted-interface preservation. You must not modify code. Later final closure review will supply all grading source, semantic/objective results, full integrity and authorization. This turn alone cannot accept the phase. No private Planner reasoning is supplied.',
 'baseline':'c1bb076e7059100f0c4b5abf623625d2843f0be2','complete_production_and_new_tests_diff':diff,
 'diff_sha256':hashlib.sha256(diff.encode()).hexdigest(),'regression':reg,
 'protected':read('final-protected.json'),'C2_preservation':read('architecture-contract-correction/accepted-checkpoint.json'),
 'correction_review_receipts':{p:{'verdict':read(p+'/review.json')['verdict'],'sha256':hashlib.sha256((out/(p+'/review.json')).read_bytes()).hexdigest()} for p in ['context-correction','authorization-correction','source-context-correction','architecture-contract-correction','planning-context-correction','contract-context-correction','analysis-transport-correction']},
 'isolation_review':read('isolation/profile-review.json'),
 'scope':'No validator weakening, accepted history edits, new orchestrator, product implementation or external effects. Seven original held-out FAILs remain unchanged. Engineering fixes are not Pello autonomous repair.'}
evidence={'objective':packet['objective'],'changed_files':['five production modules','nine protected defect-test sources'],'diff':diff+'\n\nREVIEW METADATA\n'+json.dumps({k:v for k,v in packet.items() if k!='complete_production_and_new_tests_diff'},ensure_ascii=False,separators=(',',':')),
 'test_command':reg['command'],'test_exit_code':0,'tests_run':reg['tests_run'],'tests_passed':reg['tests_run'],'tests_failed':0,
 'scope_constraints':['Code-review-only; final combined evidence review required before acceptance','No code modifications or business operations']}
length=len(json.dumps(evidence,ensure_ascii=False));print('code_review_characters',length,flush=True);assert length<=50000
(out/'final-code-review-input.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
f=read('heldout-h-freeze-v2.json');core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
 review=core.review_engineering_increment('phase3c3-review-h','3c3-final-code-h',evidence=evidence)
 result={'review':review,'diff_sha256':packet['diff_sha256'],'input_sha256':hashlib.sha256((out/'final-code-review-input.json').read_bytes()).hexdigest()}
 (out/'final-code-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True)
 assert review['verdict']=='PASS'
finally:core.backend.close()
