"""Independent complete code diff review in two bounded requests, no omissions."""
import hashlib,json,subprocess,sys
from pathlib import Path
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
class DiffReceipt(BaseModel):
    model_config=ConfigDict(extra='forbid')
    received:Literal[True]
    status:Literal['RECEIVED_NOT_A_VERDICT']
    notes:str=Field(max_length=400)
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
assert read('heldout-i-evaluation.json')['verdict']=='PASS'
reg=read('final-i-regression.json');assert reg['exit_code']==0
diff=subprocess.check_output(['git','diff','--unified=0','c1bb076e7059100f0c4b5abf623625d2843f0be2','--','athis_autopilot','tests'],text=True,encoding='utf-8')
names=subprocess.check_output(['git','diff','--name-only','c1bb076e7059100f0c4b5abf623625d2843f0be2','--','athis_autopilot','tests'],text=True,encoding='utf-8').splitlines()
first,remaining=diff[:28000],diff[28000:]
assert first+remaining==diff
manifest={'baseline':'c1bb076e7059100f0c4b5abf623625d2843f0be2','complete_diff_sha256':hashlib.sha256(diff.encode()).hexdigest(),'complete_diff_characters':len(diff),'changed_files':names,'ordered_parts':[{'index':i,'start':offset,'characters':len(s),'sha256':hashlib.sha256(s.encode()).hexdigest()} for i,offset,s in [(1,0,first),(2,len(first),remaining)]],'exact_concatenation_verified':True}
corrections=['isolation','context-correction','authorization-correction','source-context-correction','architecture-contract-correction','planning-context-correction','contract-context-correction','analysis-transport-correction','architecture-recovery']
reviews={}
for p in corrections:
    file=out/p/('profile-review.json' if p=='isolation' else 'review.json')
    reviews[p]={'verdict':json.loads(file.read_text())['verdict'],'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
receipt_packet={'objective':'Receive part 1 of the COMPLETE relevant production/test Git diff for independent final code review. This is not a verdict. Retain it in this SAME Reviewer session. The next request supplies the remainder, regression and preservation evidence, and asks you to review the complete concatenation. Do not modify code or claim approval from a receipt. No private Planner reasoning is supplied.','manifest':manifest,'diff_part_1':first}
evidence={'objective':'Independently review the ENTIRE production/test Git diff against the stated Phase 3C objectives and preservation constraints. Part 1 was provided immediately before in this same Reviewer session; part 2 follows without omissions. Evaluate both parts together. Check SDK isolation, lossless source/context transport, bounded contract merging, the single architecture recovery through guarded invocation, unchanged validators, budget/STOP/cache enforcement, and meaningful protected tests. No private Planner reasoning. Do not modify implementation. This code review alone cannot accept the phase.',
 'changed_files':names,'diff':remaining+'\n\nCOMPLETE DIFF MANIFEST AND EVIDENCE\n'+json.dumps({'manifest':manifest,'regression':reg,'protected':read('final-i-protected.json'),'correction_reviews':reviews,'preservation_proof':read('continuation114-recovery-verification.json'),'eight_original_blind_FAILs_retained':True,'engineering_corrections_not_autonomous_Pello_self_repair':True},ensure_ascii=False,separators=(',',':')),
 'test_command':reg['command'],'test_exit_code':0,'tests_run':reg['tests_run'],'tests_passed':reg['tests_run'],'tests_failed':0,
 'scope_constraints':['Planning-only closure; no business Coder execution or Phase3D','Complete diff supplied in two ordered parts in the same independent Reviewer session; final combined closure review still required']}
f=read('heldout-i-freeze.json');core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    assert len(core._prompt('final-code-i-part-1',receipt_packet))<=45000
    assert len(json.dumps(evidence,ensure_ascii=False))<=50000
    (out/'final-i-code-review-input.json').write_text(json.dumps({'part1':receipt_packet,'part2':evidence},ensure_ascii=False,indent=2),encoding='utf-8')
    ack,raw=core._invoke('phase3c3-review-i',1,'final-code-i-part-1','reviewer',receipt_packet,DiffReceipt)
    review=core.review_engineering_increment('phase3c3-review-i','3c3-final-code-i',evidence=evidence)
    result={'review':review,'diff_sha256':manifest['complete_diff_sha256'],'input_sha256':hashlib.sha256((out/'final-i-code-review-input.json').read_bytes()).hexdigest(),'part1_thread_id':raw['thread_id'],'part1_receipt':ack.model_dump(mode='json'),'manifest':manifest}
    (out/'final-i-code-review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True)
    assert review['verdict']=='PASS'
finally:core.backend.close()
