"""Author and freeze an unseen business problem in an isolated SDK session."""
import hashlib,json,os,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture

out=Path('evidence/phase3c3');private=Path(os.environ['LOCALAPPDATA'])/'PelloEvaluation'/'phase3c3-a'
private.mkdir(parents=True,exist_ok=True)
assert json.loads((out/'isolation/profile-review.json').read_text())['verdict']=='PASS'
roots=[Path(p) for p in json.loads((out/'isolation/denied-roots.json').read_text())]
roots += [Path('runtime/phase3c/projects/phase3c3-review-a').resolve(),Path('runtime/phase3c/projects/phase3c3-review-b').resolve()]
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=roots),timeout=600)
pid='phase3c3-author'
try:
    try:core.project_row(pid)
    except ValueError:
        scope=out/'AUTHOR_SCOPE.md'
        scope.write_text('# Independent held-out evaluation preparation\n\nAuthor a new synthetic business specification and freeze a private outcome rubric. Do not plan technical architecture or increments. Evaluation only; no external operations.\n')
        core.create_project(scope,project_id=pid,duration_minutes=330)
    core._role_instructions=lambda role: 'You are the independent evaluation author, outside Pello Planner context. Author a realistic business specification and evaluator-only expected-outcome rubric from the supplied preparation requirements. Do not produce a technical plan, architecture, graph, increments or manifest. Use no tools and change no files. Return only schema JSON. The rubric is hidden from the Planner.'
    payload={'objective':'Prepare a genuinely new held-out business specification that distinguishes correct autonomous planning from generic template completion. Choose a domain with capacity accounting, reconciliation or allocation over time; avoid customer case desks, returns, appointments, chatbots, toy arithmetic and workflow automation demonstrations. No existing Pello planning outputs are supplied. Make it feasible to plan independent portions even with critical uncertainty.',
        'requirements':['Multiple mandatory business capabilities and concrete numeric or temporal business rules','Operational constraints and explicit exclusions','At least one external integration with missing critical service/permission details','Dependencies between capabilities and at least two capabilities independently plannable before external integration or disputed business logic','Meaningful ambiguity plus a genuine explicit contradiction or missing safety-critical rule, with narrowly affected scope','Nonblocking reversible technical assumptions; do not pre-resolve them as customer approval','An external effect requiring a specific human authorization; specification does not itself grant execution permission','Observable acceptance examples with exact expected outcomes for clear rules; contradictory portions remain unresolved'],
        'format':'Natural-language business specification only, 2200-6500 characters. No technical decomposition or manual implementation manifest. Use clearly distinguishable paragraphs/sections. Frozen rubric 20-26 criteria with source_quote copied exactly from original spec (or empty only for generic Core structural/persistence checks). Allow multiple sound technical architectures; evaluate business semantics, not a unique expected design. Each criterion has a concrete failure condition and evidence required in the plan. Every mandatory capability, exclusion, conflict, assumption/authorization rule and independently actionable branch must have a critical criterion. Include contracts, dependency coherence, real backend model validity and accurate proposed-test claims. At most four minor criteria. All critical must pass and at least 90% overall.',
        'resource_inventory':{'local_synthetic_data':True,'python_sqlite_git':'available local capabilities; no product implementation in this evaluation','external_credentials':None,'external_service_account':None,'external_operation_authorizations':[]},
        'evaluation_id':'phase3c3-heldout-a-v1'}
    fixture,raw=core._invoke(pid,1,'author-heldout-a','tester',payload,HeldOutFixture)
    data=fixture.model_dump(mode='json');spec=fixture.specification_markdown
    assert all(not c.source_quote or c.source_quote in spec for c in fixture.rubric)
    assert len({c.criterion_id for c in fixture.rubric})==len(fixture.rubric)
    specpath=out/'heldout-a-spec.md';specbytes=spec.encode('utf-8');rubricbytes=json.dumps(data,ensure_ascii=False,sort_keys=True,indent=2).encode('utf-8')
    freeze={'evaluation_id':fixture.evaluation_id,'version':1,'created_at':datetime.now(timezone.utc).isoformat(),
        'specification_sha256':hashlib.sha256(specbytes).hexdigest(),'rubric_sha256':hashlib.sha256(rubricbytes).hexdigest(),
        'author_thread_id':raw['thread_id'],'author_turn_id':raw['turn_id'],
        'critical_criteria':sum(c.severity=='critical' for c in fixture.rubric),'total_criteria':len(fixture.rubric),
        'threshold':{'all_critical':True,'total_pass_fraction':0.9},'deny_read_roots':[str(p) for p in roots],
        'objective_check_registry':['source_hash_and_source_anchors','requirement_coverage_and_exclusions','acyclic_graph_and_valid_references','blocker_propagation_and_independent_readiness','contract_coverage_and_proposed_test_state','model_catalog_and_typed_efforts','existing_pipeline_manifest_validation','durable_restart_reconstruction_and_idempotence','no_product_implementation_or_external_effects','frozen_hidden_semantic_criteria'],
        'critical_failure_conditions':['Missing mandatory capability','Violation of explicit exclusion','Unapproved assumption treated as authorization','Ignored blocking contradiction','Invalid dependency graph','Blocked work executable','Unpermitted external effect','Incompatible existing PipelineManifest','False executed/protected product-test claim'],
        'status':'FROZEN_BEFORE_PLANNER','private_rubric_path':str(private/'rubric.json')}
    # Refuse drift on replay: freezing is append-only and happens before Planner creation.
    for path,value in [(specpath,specbytes),(private/'rubric.json',rubricbytes),(out/'heldout-a-freeze.json',(json.dumps(freeze,indent=2)+'\n').encode())]:
        if path.exists():
            if path.name=='heldout-a-freeze.json':continue
            assert path.read_bytes()==value
        else:path.write_bytes(value)
    print(json.dumps({k:v for k,v in freeze.items() if k!='private_rubric_path'},indent=2),flush=True)
finally:core.backend.close()
