"""Independent engineering review of the budget fix; not blind acceptance."""
import ast,hashlib,inspect,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3');d=out/'model-capacity-correction'
def read(name):return json.loads((out/name).read_text(encoding='utf-8'))
reg=read('model-capacity-regression.json');assert reg['exit_code']==0 and reg['tests_run']==261
integrity=read('model-capacity-integrity.json');assert integrity['historical_hashes_matching']==1493
protected=read('model-capacity-protected.json');assert all(x['exit_code']==0 and x['source_hashes_intact'] and x['protected_copy_hash_intact'] for x in protected)
protection=json.loads((d/'protection.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protection['hashes'].items())
assert hashlib.sha256(Path(protection['protected_copy']).read_bytes()).hexdigest()==protection['protected_copy_sha256']
target=(d/'targeted.log').read_text();assert re.search(r'Ran 40 tests',target) and target.rstrip().endswith('OK')
core=ProductPlanningCore(Path('runtime/phase3c'))
with core.db() as c:before=c.execute('select count(*) from pello_product_operations').fetchone()[0]
c2=core.reconstruct_plan('phase3c-3c1-live-r2');case=core.reconstruct_plan('phase3c3-heldout-i')
with core.db() as c:after=c.execute('select count(*) from pello_product_operations').fetchone()[0]
assert before==after and c2['plan_sha256']=='7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87'
assert case['plan_sha256']=='b0199c77c21c1e0b66ffd2f2b6217a011c95760bb87f0cc4957b930233c5a722' and case['approval']=='PROPOSED'
def functions(text):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
old=functions(subprocess.check_output(['git','show','94c2bb9:Pello/athis_autopilot/planning_contracts.py'],text=True,encoding='utf-8'));new=functions(Path('athis_autopilot/planning_contracts.py').read_text())
same={name:old[name]==new[name] for name in ['validate_architecture','validate_increments','validate_contracts','manifest_from_contracts','validate_model_decision','model_budget_summary']};assert all(same.values())
proof={'C2_plan_digest':c2['plan_sha256'],'I_plan_digest_unchanged':case['plan_sha256'],'I_approval':case['approval'],'counter_before':before,'counter_after':after,'unchanged_validator_converter_budget_ASTs':same,'original_nine_FAILs':{x:read(f'heldout-{x}-evaluation.json')['verdict'] for x in 'abcdefghi'},'actual_SDK_efficacy_of_capacity_fix':'UNVERIFIED; controlled-engine integration only','critical_semantic_blocker_defect':'UNRESOLVED; no source/graph/manifest edits or Validator weakening'}
assert all(v=='FAIL' for v in proof['original_nine_FAILs'].values())
(d/'objective-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
packet={'objective':'Independent engineering review of the ONE proven budget-context defect identified in your prior ParcelProof diagnosis. New model-selection requests now advertise the post-reservation capacity used by validation and aggregate reporting. Saved artifacts remain unchanged; completed missing-stage replay uses its original stored payload, with an explicit new-context marker and backward-compatible legacy pre-reservation handling. No new development capacity fails before reserving inference. Aggregate shortfall reporting, permission policy, model policy and validators remain unchanged. Critically, this does NOT repair the original semantic FAIL, interpret requirements again, regenerate the plan, demonstrate real SDK budget-fix efficacy or accept Phase3C. Review scope, real Core/SQLite controlled-engine checks, before/after evidence, historical behavior and preservation. Do not modify code or infer that tests alone prove generalization.',
 'production_diff':subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True,encoding='utf-8'),
 'complete_changed_method':inspect.getsource(ProductPlanningCore.propose_models),
 'complete_protected_tests':Path('tests/test_model_capacity_context.py').read_text(),
 'protection':protection,'complete_before_FAIL_transcript':(d/'before-FAIL.log').read_text(),'complete_targeted_transcript':target,
 'full_regression':reg,'protected_suites':protected,'objective_proof':proof,'your_independent_diagnosis':read('heldout-i-independent-failure-diagnosis.json'),'original_semantic_verdict':read('heldout-i-semantic-review.json')}
# These complete verdicts were emitted in this same Reviewer session.
# Preserve the overlimit packet; remove only repeated already-received prose.
diagnosis=read('heldout-i-independent-failure-diagnosis.json')
semantic=read('heldout-i-semantic-review.json')
packet['your_independent_diagnosis']={'same_Reviewer_thread':diagnosis['thread_id'],'complete_record_sha256':hashlib.sha256((out/'heldout-i-independent-failure-diagnosis.json').read_bytes()).hexdigest(),'context':'You emitted the complete unchanged diagnosis in your immediately prior turn in this same independent Reviewer session. It is not reprinted; code/test evidence below is complete.','classification':diagnosis['diagnosis']['classification'],'deterministic_code_defect_demonstrated':True,'critical_semantic_defect_not_repaired':True}
packet['original_semantic_verdict']={'verdict':semantic['verdict'],'critical_failures':semantic['critical_failures'],'complete_record_sha256':hashlib.sha256((out/'heldout-i-semantic-review.json').read_bytes()).hexdigest(),'context':'You emitted the full unchanged per-criterion verdict in this same Reviewer session before the diagnosis. Original FAIL remains mandatory.'}
packet['new_protected_copy_execution']=read('model-capacity-correction/protected-result.json')
evidence={'objective':packet['objective'],'changed_files':['athis_autopilot/product_planning.py','tests/test_model_capacity_context.py'],
 'diff':json.dumps({k:v for k,v in packet.items() if k!='objective'},ensure_ascii=False,separators=(',',':')),
 'test_command':'4 protected defect checks,40 focused integration/regression tests,261 full tests,63 protected C2 checks,1493 historical hashes',
 'test_exit_code':0,'tests_run':261,'tests_passed':261,'tests_failed':0,
 'scope_constraints':['Only budget-context accounting correction; do not change or accept original semantic FAIL','No fixture rerun or fresh blind evaluation; no business Coder execution, external effects or Phase3D']}
(d/'review-input.json').write_text(json.dumps(evidence,indent=2,ensure_ascii=False),encoding='utf-8')
print('review_input_characters',len(json.dumps(evidence,ensure_ascii=False)),flush=True);assert len(json.dumps(evidence,ensure_ascii=False))<=50000
f=read('heldout-i-freeze.json');core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    result=core.review_engineering_increment('phase3c3-review-i','3c3-model-capacity-correction',evidence=evidence)
    (d/'review.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2),flush=True)
    assert result['verdict']=='PASS'
finally:core.backend.close()
