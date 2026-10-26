"""Independent correction of one exact citation before freeze or Planner access."""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
from pydantic import Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.messages import Message
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture
class ExactSourceQuote(Message):
    criterion_id:str
    source_quote:str=Field(min_length=1,max_length=2500)
out=Path('evidence/phase3c3');prior=json.loads((out/'heldout-g-freeze-v2.json').read_text())
original_raw=json.loads(Path('runtime/phase3c/projects/phase3c3-author/evidence/version-1/author-heldout-h/codex_result.json').read_text())
original=HeldOutFixture.model_validate_json(original_raw['final_response']);data=original.model_dump(mode='json')
bad=[c for c in original.rubric if c.source_quote and c.source_quote not in original.specification_markdown];assert len(bad)==1 and bad[0].criterion_id=='C24'
private=Path(prior['private_rubric_path']).parents[1]/'phase3c3-h';private=private.resolve()
roots=prior['deny_read_roots']+[str(Path('runtime/phase3c/projects/phase3c3-review-h').resolve())]
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=roots),timeout=600)
try:
    with core.db() as c:assert c.execute("select count(*) from pello_product_projects where project_id='phase3c3-heldout-h'").fetchone()[0]==0
    core._role_instructions=lambda role:'You are the independent evaluation author. Repair only the exact source citation identified in your own rubric before freeze and Planner exposure. Preserve every expected outcome, severity and business specification. No technical planning or tools.'
    quote,raw=core._invoke('phase3c3-author',1,'author-heldout-h-exact-quote','tester',{'objective':'Your C24 source_quote is not an exact substring of your original specification. Return C24 and an exact supporting quote copied from the unchanged source. Do not invent a source sentence or change the expected outcome. Do not return a technical solution. No Planner output exists.',
        'original_specification':original.specification_markdown,'original_criterion':bad[0].model_dump(mode='json')},ExactSourceQuote)
    assert quote.criterion_id=='C24' and quote.source_quote in original.specification_markdown
    original_bytes=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode()
    assert not (private/'rubric-author-original.json').exists();(private/'rubric-author-original.json').write_bytes(original_bytes)
    for criterion in data['rubric']:
        if criterion['criterion_id']=='C24':criterion['source_quote']=quote.source_quote
    fixture=HeldOutFixture.model_validate(data);assert all(not c.source_quote or c.source_quote in fixture.specification_markdown for c in fixture.rubric)
    assert fixture.specification_markdown==original.specification_markdown and any(c.severity=='minor' for c in fixture.rubric)
    spec=fixture.specification_markdown.encode();rubric=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode()
    assert not (out/'heldout-h-freeze.json').exists() and not (private/'rubric.json').exists()
    (out/'heldout-h-spec.md').write_bytes(spec);(private/'rubric.json').write_bytes(rubric)
    freeze={**prior,'evaluation_id':fixture.evaluation_id,'version':1,'created_at':datetime.now(timezone.utc).isoformat(),'specification_sha256':hashlib.sha256(spec).hexdigest(),'rubric_sha256':hashlib.sha256(rubric).hexdigest(),'private_rubric_path':str(private/'rubric.json'),'deny_read_roots':roots,'author_thread_id':raw['thread_id'],'author_turn_id':raw['turn_id'],'author_original_turn_id':original_raw['turn_id'],'critical_criteria':sum(c.severity=='critical' for c in fixture.rubric),'total_criteria':len(fixture.rubric),'fresh_case_reason':'All seven prior blind cases remain consumed FAIL. Independently authored new source; no Planner output or expected technical solution supplied. One unmatched C24 quote corrected by author before freeze/Planner; source and all expected outcomes unchanged.'}
    freeze.pop('supersedes_for_first_planner_run',None);freeze.pop('change_reason',None)
    (out/'heldout-h-freeze.json').write_text(json.dumps(freeze,indent=2));print(json.dumps({k:v for k,v in freeze.items() if k!='private_rubric_path'},indent=2))
finally:core.backend.close()
