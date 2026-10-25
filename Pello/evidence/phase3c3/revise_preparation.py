"""Append-only evaluator repair before any Planner result exists."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture

out=Path('evidence/phase3c3');old=json.loads((out/'heldout-a-freeze.json').read_text());review=json.loads((out/'heldout-a-preparation-review.json').read_text())
assert review['verdict']=='FAIL'
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=old['deny_read_roots']),timeout=600)
try:
    with core.db() as cx:assert cx.execute('select count(*) from pello_product_projects where project_id=?',('phase3c3-heldout-a',)).fetchone()[0]==0
    core._role_instructions=lambda role:'You are the independent held-out evaluation author, repairing evaluation preparation before any Planner output exists. Preserve the exact business specification and all mandatory expected business outcomes. Correct the supplied independent review findings. Return required JSON; use no tools.'
    fixture,raw=core._invoke('phase3c3-author',1,'author-heldout-a-r2','tester',
        {'objective':'Create append-only evaluation version 2. The Planner has never received this specification. Preserve exact specification_markdown from your previous author output, no character changes. Preserve every mandatory business outcome as critical. Remove any particular backend architecture prescription from C24: require durable records and consistent restart behavior, allowing sound durable designs. Distinguish minor imperfections by adding 1-3 genuinely minor presentation/organization criteria that cannot hide mandatory failures; do not downgrade mandatory capability/exclusion/blocker/model/persistence criteria. Threshold all critical and at least90% total remains. evaluation_id=phase3c3-heldout-a-v2. No expected architecture, task graph or increments. No Planner results exist; reviewer found an evaluator defect, not a Pello planning defect.', 'independent_preparation_review':review},HeldOutFixture)
    assert fixture.specification_markdown.encode()==(out/'heldout-a-spec.md').read_bytes()
    assert any(c.severity=='minor' for c in fixture.rubric)
    assert all(not c.source_quote or c.source_quote in fixture.specification_markdown for c in fixture.rubric)
    private=Path(old['private_rubric_path']).parent/'rubric-v2.json'
    rubric=json.dumps(fixture.model_dump(mode='json'),ensure_ascii=False,sort_keys=True,indent=2).encode()
    assert not private.exists();private.write_bytes(rubric)
    freeze={**old,'evaluation_id':fixture.evaluation_id,'version':2,'created_at':datetime.now(timezone.utc).isoformat(),
        'rubric_sha256':hashlib.sha256(rubric).hexdigest(),'private_rubric_path':str(private),'author_thread_id':raw['thread_id'],'author_turn_id':raw['turn_id'],
        'critical_criteria':sum(c.severity=='critical' for c in fixture.rubric),'total_criteria':len(fixture.rubric),
        'supersedes_for_first_planner_run':'heldout-a-v1 preparation FAIL; original source/rubric/freeze/review preserved',
        'change_reason':'Independent preparation review, before Planner creation; no observed Planner result'}
    (out/'heldout-a-freeze-v2.json').write_text(json.dumps(freeze,indent=2)+'\n')
    print(json.dumps({k:v for k,v in freeze.items() if k!='private_rubric_path'},indent=2),flush=True)
finally:core.backend.close()
