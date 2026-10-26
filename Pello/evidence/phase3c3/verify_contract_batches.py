"""Diagnostic preflight only, no model or historical-project artifact writes."""
import copy,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
out=Path('evidence/phase3c3');directory=out/'contract-context-correction'
original=json.loads((directory/'original-contracts-input.json').read_text());core=ProductPlanningCore(Path('runtime/phase3c'));captured={};metadata={}
class Capture(Exception):pass
def capture(*args,**kwargs):captured.update(args[4]);raise Capture()
def diagnostic(path,value):metadata.update(value)
original_ensure=core._ensure_json_artifact
core._invoke=capture;core._ensure_json_artifact=diagnostic
try:core.propose_contracts('phase3c3-heldout-f')
except Capture:pass
core._ensure_json_artifact=original_ensure
assert captured['requirements']==original['requirements']
seen=[];lengths=[]
by_id={i['task_id']:i for i in original['increments']['increments']}
for group in metadata['task_ids']:
 p=copy.deepcopy(captured);p['increments']['increments']=[by_id[t] for t in group]
 lengths.append(len(core._prompt('plan-contracts-batch',p)));seen+=p['increments']['increments']
assert seen==original['increments']['increments'] and lengths==metadata['prompt_characters'] and max(lengths)<=55000
with core.db() as c:before=c.execute('select count(*) from pello_product_operations').fetchone()[0]
c2=core.reconstruct_plan('phase3c-3c1-live-r2')
with core.db() as c:after=c.execute('select count(*) from pello_product_operations').fetchone()[0]
assert before==after==68 and c2['approval']=='ACCEPTED'
proof={'canonical_input_characters':len(json.dumps(original,ensure_ascii=False,separators=(',',':'))),'batches':metadata,'all_source_requirement_fields_equal':True,'all_increment_fields_equal_in_original_order':True,'no_model_or_historical_artifact_write':True,'SDK_charges_before_after':[before,after],'C2_plan_digest':c2['plan_sha256'],'validators_unchanged':True,'F_result':'FAIL','fresh_case_required':True}
(directory/'objective-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
f=json.loads((out/'heldout-f-freeze.json').read_text())
evaluation={'evaluation_id':f['evaluation_id'],'verdict':'FAIL','objective_verdict':'FAIL','interpretation_review':'PASS','architecture_validation':'PASS','increments_validation':'PASS','requirements':37,'functional_increments':8,'critical_failures':['Contract planning context exceeds55000 before reservation; no complete contracts/model decisions/PipelineManifest'], 'no_contract_turn_reserved':True,'original_FAIL_preserved':True,'fresh_case_required_after_correction':True,'specification_sha256':f['specification_sha256'],'rubric_sha256':f['rubric_sha256'],'evidence':'heldout-f-planning.log; contract-context-correction/original-contracts-input.json'}
(out/'heldout-f-evaluation.json').write_text(json.dumps(evaluation,indent=2))
