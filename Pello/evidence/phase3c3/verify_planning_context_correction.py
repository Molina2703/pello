import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]));sys.path.insert(0,'tests')
from athis_autopilot.product_planning import ProductPlanningCore
from test_planning_context_transport import PlanningContextTransportTests
out=Path('evidence/phase3c3');directory=out/'planning-context-correction'
original=json.loads((directory/'original-increments-input.json').read_text())
core=ProductPlanningCore(Path('runtime/phase3c'));captured={}
class Capture(Exception):pass
def capture(*args,**kwargs):captured.update(args[4]);raise Capture()
core._invoke=capture
try:core.propose_increments('phase3c3-heldout-e')
except Capture:pass
assert captured['requirements']==original['requirements']
assert captured['architecture']=={k:original['architecture'][k] for k in ('nodes','global_requirement_ids')}
prompt=core._prompt('plan-increments',captured);packed=json.loads(prompt.split('DATA JSON:\n',1)[1]);packed.pop('pello_context_encoding')
assert PlanningContextTransportTests().unpack(packed)==captured
with core.db() as c:before=c.execute('select count(*) from pello_product_operations').fetchone()[0]
plan=core.reconstruct_plan('phase3c-3c1-live-r2')
with core.db() as c:after=c.execute('select count(*) from pello_product_operations').fetchone()[0]
assert before==after==61 and plan['approval']=='ACCEPTED'
assert plan['plan_sha256']=='7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87'
f=json.loads((out/'heldout-e-freeze.json').read_text())
evaluation={'evaluation_id':f['evaluation_id'],'verdict':'FAIL','objective_verdict':'FAIL','interpretation_review':'PASS','architecture_validation':'PASS','mandatory_manifest_missing':True,'critical_failures':['Increment planning context exceeded55000 before SDK reservation; no complete plan/contracts/models/manifest'],
 'requirements':40,'architecture_nodes':len(original['architecture']['nodes']),'specification_sha256':f['specification_sha256'],'rubric_sha256':f['rubric_sha256'],'original_FAIL_preserved':True,'fresh_case_required_after_correction':True,'no_additional_turn_for_context_rejection':True,'evidence':'resumed-planning-e.log; original-increments-input.json'}
(out/'heldout-e-evaluation.json').write_text(json.dumps(evaluation,indent=2))
proof={'original_json_characters':len(json.dumps(original,ensure_ascii=False,separators=(',',':'))),'corrected_prompt_characters':len(prompt),'round_trip_equal':True,'all_source_requirements_unchanged':True,'all_node_fields_and_globals_unchanged':True,'full_architecture_preserved_sha256':hashlib.sha256((core.folder('phase3c3-heldout-e')/'evidence/version-1/planning/architecture.json').read_bytes()).hexdigest(),'C2_plan_digest':plan['plan_sha256'],'SDK_charges_before_after':[before,after],'E_blind_result':'FAIL','fresh_case_required':True}
(directory/'objective-proof.json').write_text(json.dumps(proof,indent=2));print(json.dumps(proof,indent=2))
