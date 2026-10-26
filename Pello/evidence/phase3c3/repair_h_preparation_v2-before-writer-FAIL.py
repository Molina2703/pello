"""Complete independent evaluator preparation before any Planner access."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from pydantic import Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.messages import Message
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture,RubricCriterion
class PreparationRepair(Message):
    acceptance_section_markdown:str=Field(min_length=100,max_length=1600)
    revised_minor_criterion:RubricCriterion
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-h-freeze.json').read_text());original=HeldOutFixture.model_validate_json(Path(f['private_rubric_path']).read_bytes())
review=json.loads((out/'heldout-h-preparation-review-complete.json').read_text());assert review['verdict']=='FAIL'
prefix,tail=original.specification_markdown.rsplit('## Acceptance and delivery expectations',1);assert tail.strip()=='Retaining'
minor=next(c for c in original.rubric if c.criterion_id=='C26');assert minor.severity=='minor'
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    with core.db() as c:assert c.execute("select count(*) from pello_product_projects where project_id='phase3c3-heldout-h'").fetchone()[0]==0
    core._role_instructions=lambda role:'You are the independent held-out evaluation author. Repair the two preparation defects before Planner access. Preserve every existing business rule, critical rubric expectation, severity and threshold. No technical plan, architecture, graph or tools.'
    repair,raw=core._invoke('phase3c3-author',1,'author-heldout-h-preparation-v2','tester',
        {'objective':'Return only a COMPLETE short acceptance/delivery section to replace the dangling last section and revised minor criterion C26. The existing source body will remain byte-for-byte unchanged. Use a few observable examples derived from existing numeric/business rules and an explicit planning-only evidence statement; do not introduce new mandatory business rules. Keep the section under1600 characters and finish all sentences. C26 may grade minor intelligibility/presentation imperfections only, allowing all sound document organizations and technical designs; do not require grouping, cross-references, widgets or architecture unsupported by source. Keep C26 minor; all critical criteria and thresholds remain unchanged.',
         'original_complete_body':prefix,'unfinished_last_section':tail,'original_minor_criterion':minor.model_dump(mode='json'),'independent_preparation_FAIL':review},PreparationRepair)
    assert repair.revised_minor_criterion.criterion_id=='C26' and repair.revised_minor_criterion.severity=='minor'
    spec_text=prefix+'## Acceptance and delivery expectations\n\n'+repair.acceptance_section_markdown.strip()+'\n'
    assert len(spec_text)<=8500 and spec_text.startswith(prefix)
    data=original.model_dump(mode='json');data['specification_markdown']=spec_text;data['rubric']=[repair.revised_minor_criterion.model_dump(mode='json') if c['criterion_id']=='C26' else c for c in data['rubric']]
    fixture=HeldOutFixture.model_validate(data);assert all(not c.source_quote or c.source_quote in spec_text for c in fixture.rubric)
    for old,new in zip(original.rubric,fixture.rubric):
        if old.criterion_id!='C26':assert old==new
    spec=spec_text.encode();rubric=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode();private=Path(f['private_rubric_path']).with_name('rubric-v2.json')
    assert not private.exists() and not (out/'heldout-h-freeze-v2.json').exists()
    (out/'heldout-h-spec-v2.md').write_bytes(spec);private.write_bytes(rubric)
    freeze={**f,'version':2,'created_at':datetime.now(timezone.utc).isoformat(),'specification_sha256':hashlib.sha256(spec).hexdigest(),'rubric_sha256':hashlib.sha256(rubric).hexdigest(),'private_rubric_path':str(private),'author_turn_id':raw['turn_id'],'supersedes_for_first_planner_run':'heldout-h-freeze.json','change_reason':'Independent preparation FAIL preserved. Original body and all25 critical criteria unchanged; author completed dangling acceptance section with derived examples and corrected unsupported minor C26. No Planner project existed.'}
    (out/'heldout-h-freeze-v2.json').write_text(json.dumps(freeze,indent=2));print(json.dumps({k:v for k,v in freeze.items() if k!='private_rubric_path'},indent=2))
finally:core.backend.close()
