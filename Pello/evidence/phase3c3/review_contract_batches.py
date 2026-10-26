import hashlib,inspect,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from athis_autopilot.planning_contracts import validate_contracts,manifest_from_contracts
out=Path('evidence/phase3c3');d=out/'contract-context-correction';pr=json.loads((d/'protection.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pr['hashes'].items())
log=(d/'targeted.log').read_text();count=int(re.search(r'Ran (\d+) tests',log).group(1));assert count==58 and log.rstrip().endswith('OK')
diff=subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True,encoding='utf-8')
payload={'objective':'Independently review the localized contract-context correction after held-out F FAIL. Full92k input is now deterministically split into maximal ordered functional batches whose COMPLETE source/requirements and exact increment fields fit the UNCHANGED55000 cap. Every batch uses existing guarded _invoke with stable phases; responses must match exact batch task sets, then merged contracts pass the unchanged full graph/criteria/manifest validation. Preflight all batches before any reservation. Existing small whole-input phase/cache remains unchanged. Verify no source/field omission, manual technical planning, validator relaxation, history rewrite, budget bypass or false product-test claims. F remains FAIL; a fresh case is mandatory. Do not modify implementation.',
 'changed_files':['athis_autopilot/product_planning.py','tests/test_contract_context_batches.py'],
 'diff':json.dumps({'diff':diff,'complete_function':inspect.getsource(ProductPlanningCore.propose_contracts),'unchanged_validators':inspect.getsource(validate_contracts)+inspect.getsource(manifest_from_contracts),'protected_tests':Path('tests/test_contract_context_batches.py').read_text(),'protection':pr,'before_FAIL':(d/'before-FAIL.log').read_text(),'targeted_log':log,'real_rejected_input_preflight_proof':json.loads((d/'objective-proof.json').read_text()),'F_result':json.loads((out/'heldout-f-evaluation.json').read_text()),'diagnostic_setup_failure':'Initial diagnostic callback was left active during a C2 read and polluted its in-memory metadata. Raw diagnostic-setup-FAIL.json retained; callback restored before C2 verification and clean proof regenerated. No model or historical project files were written by that diagnostic.'},ensure_ascii=False,separators=(',',':')),
 'test_command':'58 targeted contract-batch/context/graph/contract/model/recovery/approval checks and real rejected-payload batch preflight',
 'test_exit_code':0,'tests_run':58,'tests_passed':58,'tests_failed':0,
 'scope_constraints':['Engineering correction only; not autonomous Pello self-repair','All six original blind FAILs preserved; no current generalization PASS','No product implementation or external business operation','Reviewer read-only; no code changes']}
(d/'review-input.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
f=json.loads((out/'heldout-f-freeze.json').read_text());core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
 review=core.review_engineering_increment('phase3c3-review-f','3c3-contract-context-batches',evidence=payload)
 (d/'review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2),flush=True)
 if review['verdict']=='PASS':(d/'accepted-checkpoint.json').write_text(json.dumps({'status':'ACCEPTED_CORRECTION_ONLY','targeted_tests':58,'review':review,'six_blind_FAILs_preserved':True,'fresh_case_required':True},indent=2))
finally:core.backend.close()
