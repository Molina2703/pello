"""Fresh independently authored fixture; CanalShare is permanently consumed."""
import hashlib,json,os,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture
from pydantic import Field
class FreshHeldOutFixture(HeldOutFixture):
    specification_markdown: str = Field(min_length=3000,max_length=6500)
out=Path('evidence/phase3c3');assert json.loads((out/'authorization-extension-101.json').read_text())['cumulative_sdk_limit']==101
assert json.loads((out/'analysis-transport-correction/review.json').read_text())['verdict']=='PASS'
prior=json.loads((out/'heldout-g-freeze-v2.json').read_text());private=Path(prior['private_rubric_path']).parents[1]/'phase3c3-h';private=private.resolve();private.mkdir(exist_ok=True)
prior['deny_read_roots']=prior['deny_read_roots']+[str(Path('runtime/phase3c/projects/phase3c3-review-h').resolve())]
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=prior['deny_read_roots']),timeout=600)
try:
    core._role_instructions=lambda role:'You are the independent held-out evaluation author. Create a new realistic business specification and hidden outcome rubric, without consulting any Planner reasoning, implementation or prior evaluation result. No technical plan, graph, increments or expected architecture. No tools. Return exact schema JSON.'
    data,raw=core._invoke('phase3c3-author',1,'author-heldout-h','tester',
        {'objective':'Create an entirely fresh held-out business scenario, substantially different from CanalShare irrigation, ArchiveLedger digital-record custody, KilnBook timber production, FolioPay royalty settlement and payments, StackProof air-permit emissions compliance, AssemblyCount cooperative meeting credentials and voting, StageMark bicycle stage-race classification, customer/return desks, appointments, HMP chatbots, ADSA and toy webhook examples. Do not retell those cases or reuse their rubrics. Choose a different operational domain; do not re-skin capacity reservations or stock reconciliation from the prior cases. Make meaningful partial planning possible while disputed or unavailable portions stay blocked.',
         'required_attributes':['Multiple mandatory business capabilities','Concrete business rules and observable acceptance examples','Operational limits and explicit exclusions','External integration with missing critical details','Capability dependencies plus at least two independently plannable capabilities','Meaningful ambiguity and at least one contradiction or missing critical requirement','Nonblocking reversible technical assumptions, explicitly not customer approval','External action requiring specific authorization; no execution permission granted'],
         'format':'Business specification in natural language, comparable realistic complexity, 3000-6500 characters within the output schema, realistic small-business scope without unnecessary repetitions, no technical decomposition. Hidden rubric 20-28 criteria, exact source_quote for business criteria, all mandatory source outcomes critical; do not invent navigation widgets, business behavior or mandatory architecture absent from source, and at least one explicitly minor presentation/clarity imperfection that does not downgrade any mandatory behavior. All critical must pass, overall fraction >=0.9. Do not require a particular persistence backend, architecture or graph; require durable behavior and appropriate contracts instead. Tests are proposed, not executed. Evaluation id phase3c3-heldout-h-v1.',
         'resources':{'local_synthetic_data':True,'local_python_sqlite_git_capabilities':True,'external_credentials':None,'external_accounts':None,'external_authorizations':[]}},FreshHeldOutFixture)
    fixture=data.model_dump(mode='json');spec=data.specification_markdown.encode('utf-8')
    assert any(c.severity=='minor' for c in data.rubric)
    assert all(not c.source_quote or c.source_quote in data.specification_markdown for c in data.rubric)
    assert hashlib.sha256(spec).hexdigest()!=prior['specification_sha256']
    rubric=json.dumps(fixture,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')
    assert not (out/'heldout-h-freeze.json').exists() and not (private/'rubric.json').exists()
    (out/'heldout-h-spec.md').write_bytes(spec);(private/'rubric.json').write_bytes(rubric)
    freeze={**prior,'evaluation_id':data.evaluation_id,'version':1,'created_at':datetime.now(timezone.utc).isoformat(),
        'specification_sha256':hashlib.sha256(spec).hexdigest(),'rubric_sha256':hashlib.sha256(rubric).hexdigest(),'private_rubric_path':str(private/'rubric.json'),
        'author_thread_id':raw['thread_id'],'author_turn_id':raw['turn_id'],'critical_criteria':sum(c.severity=='critical' for c in data.rubric),'total_criteria':len(data.rubric),
        'fresh_case_reason':'All seven prior blind runs failed and were consumed. New business source and hidden rubric independently authored after accepted generic context/schema correction; no previous Planner output supplied to author.'}
    freeze.pop('supersedes_for_first_planner_run',None);freeze.pop('change_reason',None)
    (out/'heldout-h-freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    print(json.dumps({k:v for k,v in freeze.items() if k!='private_rubric_path'},indent=2),flush=True)
finally:core.backend.close()
