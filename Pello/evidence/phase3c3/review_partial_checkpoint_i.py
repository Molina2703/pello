"""Review honest PARTIAL preservation; this cannot accept Phase3C."""
import hashlib,json,sys
from pathlib import Path
from typing import Literal
from pydantic import Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.messages import Message
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
class PreservationReview(Message):
    verdict:Literal['PASS','FAIL','BLOCKED']
    scope:Literal['partial_checkpoint_preservation_only']
    overall_phase3c:Literal['PARTIAL','BLOCKED','FAILED']
    phase_acceptance_permitted:Literal[False]
    critical_remaining_defects:list[str]=Field(min_length=1,max_length=8)
    findings:list[str]=Field(min_length=1,max_length=12)
    explanation:str=Field(max_length=3000)
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
state=read('checkpoint-107-state.json');assert state['charged_reservations']==107 and state['phase3c3']=='PARTIAL'
assert read('heldout-i-evaluation.json')['verdict']=='FAIL'
assert read('model-capacity-correction/review.json')['verdict']=='PASS'
packet={'objective':'Independent final review of HONEST PARTIAL CHECKPOINT PRESERVATION ONLY. This is not the successful Phase3C closure review: the genuine original ParcelProof FAIL is still mandatory. You previously reviewed the complete original source/rubric/plan in this SAME independent SDK session, emitted its per-criterion FAIL, diagnosed the defects, and independently accepted only the small budget correction. Verify the supplied state, actual regression, authorization, isolation, original-failure preservation and all23 conservatively scoped V1 mappings. PASS here approves preservation/reporting only and MUST NOT accept Phase3C or the business plan. No private Planner reasoning or implementation modifications are allowed. If any evidence overclaims success, return FAIL/BLOCKED. Do not grant more budget or launch another case.',
 'state_before_this_final_reserved_review':state,'expected_single_final_review_charge':{'maximum_after_completion':108,'global_cap':114,'reserve_remaining_after_completion':6},
 'latest_full_authorization':read('authorization-extension-114.json'),
 'original_frozen_source_and_rubric':read('heldout-i-freeze.json'),'preparation':read('heldout-i-preparation-accepted.json'),
 'independent_semantic_gate':read('heldout-i-evaluation.json'),'your_original_semantic_verdict':read('heldout-i-semantic-review.json'),
 'your_independent_diagnosis':read('heldout-i-independent-failure-diagnosis.json'),
 'frozen_10_objective_checks':read('heldout-i-objective.json'),'actual_contract_batching':read('heldout-i-actual-contract-batching.json'),
 'actual_SDK_isolation_audit':read('heldout-i-actual-isolation-audit.json'),
 'review_transport':{'protocol':read('review-transport-i-protocol.json'),'preflight':read('heldout-i-semantic-capacity-preflight-v3.json'),'complete_review_only_encoder_source':(out/'pack_review_i_transport.py').read_text(),'complete_original_alias_encoder_source':(out/'pack_review.py').read_text(),'note':'Only review encoding and candidate part size changed before first semantic review. Frozen original grading source unchanged; exact round trip and exact driver-text comparison verified. Source, rubric, Pello output and thresholds did not change. This did not rerun Planner.'},
 'engineering_checkpoint':read('engineering-checkpoint-i.json'),'engineering_acceptance':read('model-capacity-correction/accepted-regression-checkpoint.json'),'engineering_objective_proof':read('model-capacity-correction/objective-proof.json'),
 'full_regression':read('model-capacity-regression.json'),'protected_C2':read('model-capacity-protected.json'),'new_protected_copy':read('model-capacity-correction/protected-result.json'),'integrity':read('model-capacity-integrity.json'),
 'all23_criteria_mapping':read('criteria-coverage-i.json'),
 'remaining_limits':['Nine original blind failures remain FAIL; only ParcelProof produced a complete plan and a complete semantic score. The earlier incomplete cases have no invented score.','Original I plan remains PROPOSED, digest unchanged; no manual graph, dependency or manifest repair.','Critical blocker granularity remains unresolved; conservative validator was not weakened.','Budget correction has controlled-engine tests but no fresh real SDK held-out demonstration. I was not rerun after the implementation change.','No complete accepted blind plan, no Phase3C acceptance, no V1-20 completion or new accepted final consolidation.','Remaining capacity cannot finish a new independent case with review and reserve; no case J started.','Zero business Coder calls, messages, webhooks, customer/n8n/Railway/config/MCP mutations, or Phase3D.']}
# Keep repeated Git references once, and reference the complete verdict this
# same Reviewer already emitted. The original oversized packet is preserved.
packet['state_before_this_final_reserved_review']=dict(state)
checkpoint_rows=packet['state_before_this_final_reserved_review'].pop('checkpoints')
packet['state_before_this_final_reserved_review']['checkpoint_Git_identities_ref']='#/integrity/checkpoint_commits'
packet['state_before_this_final_reserved_review']['checkpoint_count']=len(checkpoint_rows)
packet['state_before_this_final_reserved_review']['complete_state_record_sha256']=hashlib.sha256((out/'checkpoint-107-state.json').read_bytes()).hexdigest()
semantic=read('heldout-i-semantic-review.json')
packet['your_original_semantic_verdict']={'verdict':semantic['verdict'],'critical_failures':semantic['critical_failures'],'minor_findings':semantic['minor_findings'],'critical_passed':23,'critical_total':24,'total_passed':24,'total':25,'complete_verdict_sha256':hashlib.sha256((out/'heldout-i-semantic-review.json').read_bytes()).hexdigest(),'context':'You emitted the complete unchanged25-row semantic verdict in this SAME independent Reviewer session after receiving every evidence part. The original FAIL and critical C13 grade are preserved. No criterion is rescored or removed from the original record.'}
(out/'partial-i-final-review-input.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False),encoding='utf-8')
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=read('heldout-i-freeze.json')['deny_read_roots']),timeout=600)
try:
    assert len(core._prompt('partial-i-checkpoint-final-review',packet))<=55000
    result,raw=core._invoke('phase3c3-review-i',1,'partial-i-checkpoint-final-review','reviewer',packet,PreservationReview)
    record={'review':result.model_dump(mode='json'),'thread_id':raw['thread_id'],'turn_id':raw['turn_id'],'reviewed_input_sha256':hashlib.sha256((out/'partial-i-final-review-input.json').read_bytes()).hexdigest(),'Phase3C_accepted':False}
    (out/'partial-i-final-review.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record,indent=2),flush=True)
    assert result.verdict=='PASS' and result.overall_phase3c=='PARTIAL'
finally:core.backend.close()
