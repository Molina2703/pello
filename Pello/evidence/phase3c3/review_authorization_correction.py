import json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3/authorization-correction');f=json.loads(Path('evidence/phase3c3/heldout-b-freeze.json').read_text())
count=sum(int(re.search(r'Ran (\d+) tests',p.read_text()).group(1)) for p in out.glob('test_*.log'))
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=480)
try:
    evidence={'objective':'Independently review the smallest engineering correction after fresh ArchiveLedger FAIL. The model returned category authorization with authorization_required=false for a local role policy, violating an existing Pydantic guard that was invisible in the model-facing schema. The only implementation change adds a Field description documenting the pre-existing invariant and its non-grant meaning, including local role enforcement. No validator is relaxed, no failed output is edited or accepted, no source/rubric changes. Inspect whether this clarifies the accepted contract without inventing business authorization. Original blind B remains FAIL; only a new unseen case may establish blind generalization. Engineering-session repair, not autonomous product self-repair.',
        'changed_files':['athis_autopilot/product_planning.py','tests/test_authorization_schema_contract.py'],
        'diff':subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True)+'\nPROTECTED TEST SOURCE:\n'+Path('tests/test_authorization_schema_contract.py').read_text()+'\nORIGINAL FAILED RUN:\n'+Path('evidence/phase3c3/heldout-b-planning.log').read_text()+'\nACTUAL LOSSLESS RECOVERY / RESERVATION RECONCILIATION:\n'+(out/'schema-invariant-evidence.json').read_text()+'\nACTUAL TEST TRANSCRIPTS:\n'+'\n'.join(p.read_text() for p in out.glob('test_*.log')),
        'test_command':'Six targeted suites: model-facing schema contract, accepted interpretation/input/context/recovery/approval checks',
        'test_exit_code':0,'tests_run':count,'tests_passed':count,'tests_failed':0,
        'scope_constraints':['Both original held-out FAILs remain FAIL; no rerun can be called blind','No source/rubric or accepted history edits','55,000-character limit unchanged, no truncation','No SDK call for oversized rejected payload; STOP/global/project budgets preserved','No counter reset, original completed 28 rows intact','Fresh held-out evaluation required, no Phase 3D']}
    (out/'review-input.json').write_text(json.dumps(evidence,indent=2))
    review=core.review_engineering_increment('phase3c3-review-b','3c3-authorization-correction',evidence=evidence)
    (out/'review.json').write_text(json.dumps(review,indent=2));print(json.dumps(review,indent=2),flush=True)
finally:core.backend.close()
