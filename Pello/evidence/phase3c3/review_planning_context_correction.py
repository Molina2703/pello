import hashlib,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3');directory=out/'planning-context-correction'
protection=json.loads((directory/'protection.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protection['hashes'].items())
log=(directory/'targeted.log').read_text();count=int(re.search(r'Ran (\d+) tests',log).group(1));assert log.rstrip().endswith('OK') and count==53
diff=subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True,encoding='utf-8')
source=Path('athis_autopilot/product_planning.py').read_text();code=source[source.index('    def propose_increments'):source.index('    def propose_contracts')]+source[source.index('    @staticmethod\n    def _prompt'):source.index('    def understand')]
payload={'objective':'Independent review of a small context-bound correction after held-out E FAIL. Evaluate whether increment planning needs only exact validated nodes/global IDs plus the complete accepted requirement/source/issue/assumption set, while the full narrative architecture remains immutable and later validations use it. Assess generic lossless table transport only for oversized plan-* inputs: no source/field/value loss, marker-collision failure, original journal identity, unchanged55000 cap and unchanged small inputs. No validators, budgets, authorization or semantic rubric may be weakened. E remains FAIL; a new independently authored held-out is required. This is engineering repair, not Pello autonomous self-repair.',
 'changed_files':['athis_autopilot/product_planning.py','tests/test_planning_context_transport.py'],
 'diff':json.dumps({'diff':diff,'complete_relevant_functions':code,'protected_test_source':Path('tests/test_planning_context_transport.py').read_text(),'protection':protection,'before_failure':(directory/'before-FAIL.log').read_text(),'targeted_results':log,'objective_proof':json.loads((directory/'objective-proof.json').read_text()),'original_E_result':json.loads((out/'heldout-e-evaluation.json').read_text()),'test_setup_error_retained':'targeted-setup-FAIL.log was a wrong-module/import invocation; corrected targeted command passes53 without test edits'},ensure_ascii=False,separators=(',',':')),
 'test_command':'53 targeted transport/context/graph/increment/acceptance/model/recovery/approval tests; real rejected input round-trip proof; C2 reconstruction',
 'test_exit_code':0,'tests_run':count,'tests_passed':count,'tests_failed':0,
 'scope_constraints':['No implementation of StackProof or external operations','Frozen E source/rubric and original FAIL preserved','Review only; do not modify code','Fresh evaluation before any generalization claim']}
(directory/'review-input.json').write_text(json.dumps(payload,indent=2),encoding='utf-8')
f=json.loads((out/'heldout-e-freeze.json').read_text());core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
 review=core.review_engineering_increment('phase3c3-review-e','3c3-planning-context-correction',evidence=payload)
 (directory/'review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2),flush=True)
 if review['verdict']=='PASS':(directory/'accepted-checkpoint.json').write_text(json.dumps({'status':'ACCEPTED_CORRECTION_ONLY','targeted_tests':53,'review':review,'proof':json.loads((directory/'objective-proof.json').read_text()),'five_original_blind_FAILs_preserved':True,'fresh_case_required':True},indent=2))
finally:core.backend.close()
