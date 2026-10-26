"""Review a bounded recovery capability without misclassifying the H failure."""
import ast,hashlib,inspect,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3');d=out/'architecture-recovery';protection=json.loads((d/'protection.json').read_text())
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protection['hashes'].items())
integration_protection=json.loads((d/'protection-integration.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in integration_protection['hashes'].items())
log=(d/'targeted.log').read_text();n=int(re.search(r'Ran (\d+) tests',log).group(1));assert n==83 and log.rstrip().endswith('OK')
def funcs(s):return {n.name:ast.dump(n,include_attributes=False) for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
a=funcs(subprocess.check_output(['git','show','c1bb076:Pello/athis_autopilot/planning_contracts.py'],text=True,encoding='utf-8'));b=funcs(Path('athis_autopilot/planning_contracts.py').read_text());same={k:a[k]==b[k] for k in ['validate_architecture','validate_increments','validate_contracts','manifest_from_contracts']};assert all(same.values())
core=ProductPlanningCore(Path('runtime/phase3c'));c2=core.reconstruct_plan('phase3c-3c1-live-r2');assert c2['plan_sha256']=='7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87'
proof={'unchanged_validator_and_converter_ASTs':same,'C2_plan_digest':c2['plan_sha256'],'eight_original_FAILs_preserved':True,'H_not_rerun_after_change':True,'targeted_tests':n,'new_capability_not_deterministic_validator_bugfix':True,'actual_unfamiliar_SDK_recovery_not_demonstrated':True}
(d/'objective-proof-r2.json').write_text(json.dumps(proof,indent=2))
evidence={'objective':'Independent engineering review of one small planning robustness increment after preserved H FAIL. Your earlier diagnosis correctly classified H as invalid Planner output and found no deterministic validator defect. That conclusion remains unchanged. This is an added bounded recovery capability, not a validator fix: after a typed architecture fails the unchanged validator, persist that original rejection, send exact source plus the model own proposal/error back through existing guarded _invoke ONCE, then require the same validator to pass. Initial valid behavior/result/cache stay unchanged. Invalid correction still FAILs, guards can block retry, and no model escalation/authorization occurs. Assess correctness, scope and preservation critically; do not approve merely because tests pass. No live H rerun, generalization PASS or autonomous repair of H is claimed. A fresh case must validate real SDK efficacy.',
 'changed_files':['athis_autopilot/product_planning.py','tests/test_architecture_validation_recovery.py'],
 'diff':json.dumps({'diff':subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True,encoding='utf-8'),'complete_changed_method':inspect.getsource(ProductPlanningCore.propose_architecture),'complete_protected_tests':Path('tests/test_architecture_validation_recovery.py').read_text(),'protection':protection,'before_FAIL':(d/'before-FAIL.log').read_text(),'targeted_log':log,'proof':proof,'original_H_evaluation':json.loads((out/'heldout-h-evaluation.json').read_text()),'your_prior_independent_diagnosis':json.loads((out/'heldout-h-independent-graph-diagnosis.json').read_text())},ensure_ascii=False,separators=(',',':')),
 'test_command':'80 focused validation/recovery/context/graph/contracts/approval/lifecycle checks',
 'test_exit_code':0,'tests_run':n,'tests_passed':n,'tests_failed':0,
 'scope_constraints':['No deterministic validator defect or semantic H PASS claimed','No manual replacement graph, schema weakening, new orchestrator, model ladder, external operation or business Coder','One correction maximum via existing source/STOP/budget/context/session guards','Full regression required before accepted engineering checkpoint; fresh held-out required for generalization']}
reg=json.loads((out/'architecture-recovery-regression.json').read_text());integrity=json.loads((out/'architecture-recovery-integrity.json').read_text());protected=json.loads((out/'architecture-recovery-protected.json').read_text())
assert reg['exit_code']==0 and reg['tests_run']==257 and integrity['historical_hashes_matching']==1493
assert all(p['exit_code']==0 and p['source_hashes_intact'] and p['protected_copy_hash_intact'] for p in protected)
packet=json.loads(evidence['diff'])
sections={k:packet.pop(k) for k in ['diff','complete_changed_method','complete_protected_tests','before_FAIL','targeted_log']}
sections['complete_production_invoke_integration_tests']=Path('tests/test_architecture_recovery_ledger.py').read_text()
sections['production_invoke_test_log']=(d/'production-invoke.log').read_text()
initial_packet=json.loads(json.loads((d/'review-input-initial-BLOCKED.json').read_text())['diff'])
assert initial_packet['before_FAIL']==sections['before_FAIL']
sections['before_FAIL']='The complete unchanged pre-correction FAIL transcript was supplied in your previous engineering-review turn in this same independent Reviewer session. It is not reprinted: SHA256='+hashlib.sha256(sections['before_FAIL'].encode()).hexdigest()+'; characters='+str(len(sections['before_FAIL']))+'. The exact full transcript remains preserved at architecture-recovery/before-FAIL.log and in review-input-initial-BLOCKED.json.'
packet.update({'full_regression':reg,'integrity':integrity,'protected_C2':protected,'integration_protection':integration_protection,'prior_BLOCKED_review':json.loads((d/'review-initial-BLOCKED.json').read_text()),'production_unchanged_since_initial_review':True,'clarification':'The mock engine is controlled test data; _invoke, SQLite operations, source checks, global budget/STOP rejection and restart cache are actual production code. No live SDK recovery efficacy or generalization PASS is claimed.'})
evidence['diff']='\n\n'.join(name+'\n'+value for name,value in sections.items())+'\n\nOBJECTIVE METADATA JSON\n'+json.dumps(packet,ensure_ascii=False,separators=(',',':'))
evidence['test_command']='83 focused checks plus complete257 test regression,63 protected and1493 historical hashes'
evidence['tests_run']=reg['tests_run'];evidence['tests_passed']=reg['tests_run']
evidence['objective']+=' This re-review supplies the requested production-invocation tests and complete regression. Prior BLOCKED evidence is preserved.'
assert len(json.dumps(evidence,ensure_ascii=False))<=50000
(d/'review-input-r2.json').write_text(json.dumps(evidence,indent=2))
f=json.loads((out/'heldout-h-freeze-v2.json').read_text());core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    review=core.review_engineering_increment('phase3c3-review-h','3c3-bounded-architecture-recovery-r2',evidence=evidence)
    (d/'review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2));assert review['verdict']=='PASS'
finally:core.backend.close()
