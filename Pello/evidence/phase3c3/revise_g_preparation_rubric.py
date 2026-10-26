"""Independent pre-Planner correction of an unsupported evaluator expectation."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture,RubricCriterion
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-g-freeze.json').read_text())
original=HeldOutFixture.model_validate_json(Path(f['private_rubric_path']).read_bytes())
finding=json.loads((out/'heldout-g-preparation-review-complete.json').read_text());assert finding['verdict']=='FAIL'
criterion=next(c for c in original.rubric if c.criterion_id=='C18')
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    with core.db() as c:assert c.execute("select count(*) from pello_product_projects where project_id='phase3c3-heldout-g'").fetchone()[0]==0
    core._role_instructions=lambda role:'You are the independent held-out evaluation author. Correct only the identified unsupported rubric expectation before Planner access. Do not create any technical plan or access tools. Preserve mandatory source behavior, severity and thresholds.'
    amended,raw=core._invoke('phase3c3-author',1,'author-heldout-g-rubric-r2','tester',
        {'objective':'Revise C18 only to remove the unsupported requirement for actionable navigation links. Require the original observable screen exposure behavior without prescribing layout/navigation. Preserve source quote, criterion identity, critical severity, and every source-required outcome. No Planner has seen the case and no Planner output is provided.',
         'original_specification':original.specification_markdown,'original_criterion':criterion.model_dump(mode='json'),'independent_preparation_review':finding},RubricCriterion)
    assert amended.criterion_id==criterion.criterion_id and amended.severity==criterion.severity and amended.source_quote==criterion.source_quote and amended.area==criterion.area
    data=original.model_dump(mode='json');data['rubric']=[amended.model_dump(mode='json') if c['criterion_id']=='C18' else c for c in data['rubric']]
    fixture=HeldOutFixture.model_validate(data)
    assert fixture.specification_markdown==original.specification_markdown
    rubric=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode();path=Path(f['private_rubric_path']).with_name('rubric-v2.json');assert not path.exists();path.write_bytes(rubric)
    updated={**f,'version':2,'created_at':datetime.now(timezone.utc).isoformat(),'rubric_sha256':hashlib.sha256(rubric).hexdigest(),'private_rubric_path':str(path),'author_turn_id':raw['turn_id'],'supersedes_for_first_planner_run':'heldout-g-freeze.json','change_reason':'Independent preparation FAIL: unsupported navigation-link requirement in C18. Author corrected C18 only before any Planner access. Original source, all other criteria and thresholds unchanged.'}
    (out/'heldout-g-freeze-v2.json').write_text(json.dumps(updated,indent=2));print(json.dumps({k:v for k,v in updated.items() if k!='private_rubric_path'},indent=2))
finally:core.backend.close()
