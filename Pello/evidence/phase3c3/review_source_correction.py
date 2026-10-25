import inspect,json,re,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3/source-context-correction');f=json.loads(Path('evidence/phase3c3/heldout-c-freeze.json').read_text())
logs=[p.read_text() for p in out.glob('test_*.log')];count=sum(int(re.search(r'Ran (\d+) tests',s).group(1)) for s in logs)
assert count==59 and all(s.rstrip().endswith('OK') for s in logs)
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=480)
try:
    evidence={'objective':'Independently review final localized context correction after original held-out C FAIL. Prior map deduplication still left the full original Markdown duplicated as map text. The existing 55,000 limit remains. Only exact canonical source-map texts matching their inclusive source line spans may be represented by line references to the complete original source, which remains supplied once. No requirement/issue/assumption, rubric, source text or validator is weakened or truncated. Canonical journal payload and replay identities are unchanged. New unit checks cover complete round-trip reconstruction, CRLF and refusal to hide nonmatching source text. Original A/B/C blind runs remain FAIL; no generalization PASS claimed. Engineering-session correction only. A new case requires enough explicitly authorized budget including a failure reserve.',
        'changed_files':['athis_autopilot/product_planning.py','tests/test_review_source_references.py'],
        'diff':subprocess.check_output(['git','diff','--','athis_autopilot/product_planning.py'],text=True)+'\nCOMPLETE CURRENT PACKER:\n'+inspect.getsource(ProductPlanningCore._prompt)+'\nPROTECTED NEW TEST:\n'+Path('tests/test_review_source_references.py').read_text()+'\nORIGINAL ACTUAL FAIL:\n'+Path('evidence/phase3c3/heldout-c-planning.log').read_text()+'\nACTUAL FULL-PAYLOAD ROUND TRIP:\n'+(out/'actual-lossless-proof.json').read_text()+'\nTARGETED TEST TRANSCRIPTS:\n'+'\n'.join(logs),
        'test_command':'Seven targeted interpretation/context/schema/input/recovery/approval suites',
        'test_exit_code':0,'tests_run':count,'tests_passed':count,'tests_failed':0,
        'scope_constraints':['No acceptance override; three original blind FAILs preserved','No counter reset; prior never-submitted charge retained','No external effects or Phase 3D','Full original source retained; exact line-reference reconstruction only','New blind case only after sufficient authorization']}
    (out/'review-input.json').write_text(json.dumps(evidence,indent=2))
    result=core.review_engineering_increment('phase3c3-review-c','3c3-source-context-correction',evidence=evidence)
    (out/'review.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
finally:core.backend.close()
