import json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3/context-correction');f=json.loads(Path('evidence/phase3c3/heldout-a-freeze-v2.json').read_text())
count=sum(int(re.search(r'Ran (\d+) tests',p.read_text()).group(1)) for p in out.glob('test_*.log'))
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=480)
try:
    evidence={'objective':'Independent review of smallest Core correction justified by original held-out FAIL. Do not accept Phase 3C or the failed CanalShare planning run. Review only lossless duplicated-source factoring at the unchanged 55,000-character review boundary and validation BEFORE SDK reservation. Canonical payload, journal identity, contracts and accepted historical replay remain unchanged. Previously reserved but never submitted operation is reconciled with its original row preserved; its used_turns charge is NOT decremented. A new independent held-out case is mandatory after this repair. This engineering session made the repair; it was not Pello autonomous business-product self-repair.',
        'changed_files':['athis_autopilot/product_planning.py','tests/test_planning_context_budget.py'],
        'diff':subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True)+'\nPROTECTED TEST SOURCE:\n'+Path('tests/test_planning_context_budget.py').read_text()+'\nORIGINAL FAILED RUN:\n'+Path('evidence/phase3c3/heldout-a-planning.log').read_text()+'\nACTUAL LOSSLESS RECOVERY / RESERVATION RECONCILIATION:\n'+(out/'reservation-reconciliation.json').read_text()+'\nACTUAL TEST TRANSCRIPTS:\n'+'\n'.join(p.read_text() for p in out.glob('test_*.log')),
        'test_command':'Five targeted suites, including frozen new context/budget regression and accepted interpretation/input/recovery/approval integration suites',
        'test_exit_code':0,'tests_run':count,'tests_passed':count,'tests_failed':0,
        'scope_constraints':['Original held-out FAIL remains FAIL; no rerun can be called blind','No source/rubric or accepted history edits','55,000-character limit unchanged, no truncation','No SDK call for oversized rejected payload; STOP/global/project budgets preserved','No counter reset, original completed 28 rows intact','Fresh held-out evaluation required, no Phase 3D']}
    (out/'review-input.json').write_text(json.dumps(evidence,indent=2))
    review=core.review_engineering_increment('phase3c3-review-a','3c3-context-correction',evidence=evidence)
    (out/'review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2),flush=True)
finally:core.backend.close()
