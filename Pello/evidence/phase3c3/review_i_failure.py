"""Independent diagnosis of the consumed FAIL; no plan repair or acceptance."""
import hashlib,inspect,json,sys
from pathlib import Path
from typing import Literal
from pydantic import Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.messages import Message
from athis_autopilot.product_planning import ProductPlanningCore,PLANNER_INSTRUCTIONS
from athis_autopilot.ai_supervisor import SDKBackend
from athis_autopilot.planning_contracts import validate_architecture
class FailureDiagnosis(Message):
    classification:Literal['planner_output','requirement_interpretation','validator','planning_context_contract','mixed','uncertain']
    original_FAIL_justified:bool
    critical_findings:list[str]=Field(min_length=1,max_length=8)
    earliest_failure_stage:str
    deterministic_code_defect_demonstrated:bool
    implementation_change_justified:bool
    smallest_generic_remediation:str=Field(max_length=3000)
    budget_finding:str=Field(max_length=2000)
    explanation:str=Field(max_length=3000)
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-i-freeze.json').read_text())
assert json.loads((out/'heldout-i-evaluation.json').read_text())['verdict']=='FAIL'
p=json.loads((out/'heldout-i-plan.json').read_text())['plan'];a=p['requirements']
issues=[i for i in a['issues'] if i['issue_id'] in ['ISS-f1ee3142ec14','ISS-bf95e4f6bde7']]
ids={r for i in issues for r in i['affected_requirement_ids']}
packet={'objective':'Independently diagnose the original ParcelProof semantic FAIL you just graded in this same session. Locate the EARLIEST real defect, distinguish Planner reasoning from deterministic validator/transport/context defects, and decide whether a small implementation correction is justified. Do not repair this plan, give a replacement graph or assign requirement IDs to replacement nodes. Do not weaken validators, exempt local work from genuine blockers, alter source/rubric, invent resolution or approval, or call a narrative claim executable. A model-output error alone is not proof of a validator bug. No production changes should be recommended merely to obtain PASS. If only generic guidance or future deeper semantic validation is supported, say so. Evaluate the separate one-turn budget discrepancy against the actual request and validation code. No private Planner reasoning is supplied. The case remains FAIL regardless of diagnosis.',
 'original_source':(out/'heldout-i-spec.md').read_text(),
 'semantic_verdict':json.loads((out/'heldout-i-semantic-review.json').read_text()),
 'affected_interpretation':{'issues':issues,'requirements':[r for r in a['requirements'] if r['requirement_id'] in ids]},
 'architecture_nodes':p['stages']['architecture']['proposal']['nodes'],
 'enforced_graph':p['stages']['architecture']['validation'],
 'validator_source':inspect.getsource(validate_architecture),
 'current_architecture_pipeline_source':inspect.getsource(ProductPlanningCore.propose_architecture),
 'analyst_instructions':PLANNER_INSTRUCTIONS,
 'model_stage_source':inspect.getsource(ProductPlanningCore.propose_models),
 'model_budget_request_value':json.loads((Path('runtime/phase3c/projects/phase3c3-heldout-i/evidence/version-1/plan-models/input.json')).read_text())['development_turns_remaining'],
 'model_budget_result':p['stages']['models']['aggregate_budget_assessment'],
 'scope':'One new held-out case was authorized and consumed; no fresh follow-up case has enough capacity. Only the smallest proven correction, protected checks, regression and independent engineering review may be considered. No business implementation, no Phase3D.'}
(out/'heldout-i-failure-diagnosis-input.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False),encoding='utf-8')
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    result,raw=core._invoke('phase3c3-review-i',1,'heldout-i-failure-diagnosis','reviewer',packet,FailureDiagnosis)
    record={'diagnosis':result.model_dump(mode='json'),'thread_id':raw['thread_id'],'turn_id':raw['turn_id'],'input_sha256':hashlib.sha256((out/'heldout-i-failure-diagnosis-input.json').read_bytes()).hexdigest(),'original_I_verdict':'FAIL'}
    (out/'heldout-i-independent-failure-diagnosis.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(json.dumps(record,indent=2),flush=True)
finally:core.backend.close()
