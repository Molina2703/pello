import inspect,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3/architecture-contract-correction');f=json.loads(Path('evidence/phase3c3/heldout-d-freeze.json').read_text())
logs=[p.read_text() for p in out.glob('test_*.log')];count=sum(int(re.search(r'Ran (\d+) tests',s).group(1)) for s in logs)
assert count==55 and all(s.rstrip().endswith('OK') for s in logs)
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=480)
try:
    evidence={'objective':'Independently review a minimal model-facing architecture contract clarification after original fresh D FAIL. Architecture global IDs incorrectly included a business_rule; local provided inputs were represented as unavailable resource prerequisites. Existing Core enforcement is unchanged. Only two Field descriptions expose category eligibility and distinguish separately missing resources from provided local capabilities, input rules and future task outputs. Do not relax validators or accept the rejected architecture. No case-specific IDs, nodes, dependencies or expected solution are supplied to Planner. Original A/B/C/D remain FAIL. New explicit 75-turn grant preserves counters and allows another fresh case. Assess clarity, compatibility and safety; this metadata correction is not proof of planning generalization.',
        'changed_files':['athis_autopilot/planning_contracts.py','tests/test_architecture_schema_contract.py'],
        'diff':subprocess.check_output(['git','diff','--','athis_autopilot/planning_contracts.py'],text=True)+'\nCOMPLETE CURRENT PACKER:\n'+inspect.getsource(__import__('athis_autopilot.planning_contracts',fromlist=['validate_architecture']).validate_architecture)+'\nPROTECTED NEW TEST:\n'+Path('tests/test_architecture_schema_contract.py').read_text()+'\nORIGINAL ACTUAL FAIL:\n'+Path('evidence/phase3c3/heldout-d-planning.log').read_text()+'\nACTUAL FULL-PAYLOAD ROUND TRIP:\n'+(out/'contract-discoverability-proof.json').read_text()+'\nTARGETED TEST TRANSCRIPTS:\n'+'\n'.join(logs),
        'test_command':'Seven targeted architecture/increment/contract/model/persistence/approval suites',
        'test_exit_code':0,'tests_run':count,'tests_passed':count,'tests_failed':0,
        'scope_constraints':['No acceptance override; four original blind FAILs preserved','No counter reset; prior never-submitted charge retained','No external effects or Phase 3D','Full original source retained; exact line-reference reconstruction only','New blind case only after sufficient authorization']}
    (out/'review-input.json').write_text(json.dumps(evidence,indent=2))
    result=core.review_engineering_increment('phase3c3-review-d','3c3-architecture-contract-correction',evidence=evidence)
    (out/'review.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
finally:core.backend.close()
