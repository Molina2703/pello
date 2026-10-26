"""Independent review of the localized, protected review-context correction."""
import ast,hashlib,inspect,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3');d=out/'analysis-transport-correction'
pr=json.loads((d/'protection.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pr['hashes'].items())
original=(d/'original-review-input.json').read_bytes();assert hashlib.sha256(original).hexdigest()==pr['fixture_sha256']
log=(d/'targeted.log').read_text();n=int(re.search(r'Ran (\d+) tests',log).group(1));assert n==83 and log.rstrip().endswith('OK')
payload=json.loads(original);prompt=ProductPlanningCore._prompt('review-analysis',payload);assert len(prompt)<=55000
core=ProductPlanningCore(Path('runtime/phase3c'))
with core.db() as c:before=c.execute('select count(*) from pello_product_operations').fetchone()[0]
c2=core.reconstruct_plan('phase3c-3c1-live-r2');assert c2['plan_sha256']=='7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87'
with core.db() as c:after=c.execute('select count(*) from pello_product_operations').fetchone()[0]
assert before==after==74
def functions(source):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(source).body if isinstance(n,ast.FunctionDef)}
baseline=functions(subprocess.check_output(['git','show','c1bb076:Pello/athis_autopilot/planning_contracts.py'],text=True,encoding='utf-8'))
current=functions(Path('athis_autopilot/planning_contracts.py').read_text())
validators={k:baseline[k]==current[k] for k in ['validate_architecture','validate_increments','validate_contracts','manifest_from_contracts']};assert all(validators.values())
proof={'prompt_characters':len(prompt),'exact_round_trip_and_input_immutability_tests':'83 targeted PASS includes exact original StageMark replay for initial and revision review phases','canonical_fixture_sha256':hashlib.sha256(original).hexdigest(),'C2_digest':c2['plan_sha256'],'SDK_count_before_after':[before,after],'validators_unchanged':validators,'G_original_verdict':'FAIL','new_blind_case_required':True,'no_G_retry':True}
(d/'objective-proof.json').write_text(json.dumps(proof,indent=2))
diff=subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True,encoding='utf-8')
evidence={'objective':'Independently review only the localized interpretation-review context correction after genuine held-out G FAIL. Existing review source factoring reduced the complete canonical78267 input to57430, still above unchanged55000. Apply the already accepted reversible table encoder to the CURRENT factored review JSON as well as planning phases: final45441. Preserve exact source and all42 requirements/9 issues/3 assumptions, all values, references, no input mutation, reserved-marker rejection and oversized rejection before reservation. Full validator/converter ASTs unchanged. No schema/model/rubric change, new orchestrator or business implementation. G must remain FAIL; no corrected same-case run counts as blind or autonomous self-repair. Do not modify implementation.',
 'changed_files':['athis_autopilot/product_planning.py','tests/test_analysis_review_transport.py'],
 'diff':json.dumps({'diff':diff,'complete_prompt_function':inspect.getsource(ProductPlanningCore._prompt),'complete_protected_tests':Path('tests/test_analysis_review_transport.py').read_text(),'protection':pr,'original_diagnosis':json.loads((d/'diagnosis.json').read_text()),'before_FAIL':(d/'before-FAIL.log').read_text(),'targeted_log':log,'proof':proof,'original_evaluation':json.loads((out/'heldout-g-evaluation.json').read_text()),'targeted_setup_failure':'First targeted command used one nonexistent module alias and omitted tests import path. Original setup FAIL retained; corrected command passed83. No protected test or implementation workaround was used.'},ensure_ascii=False,separators=(',',':')),
 'test_command':'83 focused context/source/contract/graph/approval/lifecycle checks with tests import path',
 'test_exit_code':0,'tests_run':n,'tests_passed':n,'tests_failed':0,
 'scope_constraints':['Engineering correction only, not generalization PASS','Seven original held-out FAILs preserved','No product Coder or external effects, no Phase3D','Full regression required before accepted checkpoint']}
(d/'review-input.json').write_text(json.dumps(evidence,indent=2));assert len(json.dumps(evidence,ensure_ascii=False))<=50000
f=json.loads((out/'heldout-g-freeze-v2.json').read_text());core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    review=core.review_engineering_increment('phase3c3-review-g','3c3-analysis-context-transport',evidence=evidence)
    (d/'review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2));assert review['verdict']=='PASS'
finally:core.backend.close()
