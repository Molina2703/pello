"""Supplement the frozen objective gates with actual contract transport receipts."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
out=Path('evidence/phase3c3');core=ProductPlanningCore(Path('runtime/phase3c'))
pid='phase3c3-heldout-i';payload=core.planner_input(pid)
directory=core.folder(pid)/'evidence/version-1';planning=directory/'planning'
canonical=core.planning_stage(pid,'increments')['proposal']['increments']
globals_=core.planning_stage(pid,'architecture')['proposal']['global_requirement_ids']
merged=core.planning_stage(pid,'contracts')['proposal']['contracts']
batching=planning/'contracts-context-batches.json'
phases=[f'plan-contracts-b{i}' for i in range(1,len(json.loads(batching.read_text())['task_ids'])+1)] if batching.exists() else ['plan-contracts']
all_items=[];all_contracts=[];checks=[]
for phase in phases:
    folder=directory/phase;part=json.loads((folder/'input.json').read_text())
    prompt=(folder/'codex_prompt.txt').read_text(encoding='utf-8')
    result=json.loads((folder/'codex_result.json').read_text())
    contracts=json.loads(result['final_response'])['contracts']
    items=part['increments']['increments'];all_items.extend(items);all_contracts.extend(contracts)
    checks.append({'phase':phase,'complete_requirements_exact':part['requirements']==payload['requirements'],
        'source_hash_exact':part['source_sha256']==payload['source_sha256'],
        'global_requirements_exact':part['global_requirement_ids']==globals_,
        'submitted_prompt_exact':prompt==core._prompt(phase,part),'prompt_characters':len(prompt),'within_preflight_limit':len(prompt)<=55000,
        'exact_batch_task_coverage':{x['task_id'] for x in items}=={x['task_id'] for x in contracts} and len(items)==len(contracts),
        'input_sha256':hashlib.sha256((folder/'input.json').read_bytes()).hexdigest(),
        'prompt_sha256':hashlib.sha256((folder/'codex_prompt.txt').read_bytes()).hexdigest(),
        'response_sha256':hashlib.sha256((folder/'codex_result.json').read_bytes()).hexdigest()})
assert all(all(v for k,v in x.items() if k.endswith(('_exact','_coverage','_limit'))) for x in checks)
ids=[c['criterion_id'] for contract in merged for c in contract['criteria']]
result={'verdict':'PASS','batches':checks,'all_increment_fields_and_order_exact':all_items==canonical,'merged_contracts_exactly_equal_all_batch_responses':all_contracts==merged,'unique_criterion_ids':len(ids)==len(set(ids)),'merged_contracts':len(merged),'proposed_criteria':len(ids),'aggregate_existing_validation':core.planning_stage(pid,'contracts')['validation'],'no_business_implementation_or_tests_executed':True}
assert result['all_increment_fields_and_order_exact'] and result['merged_contracts_exactly_equal_all_batch_responses'] and result['unique_criterion_ids']
(out/'heldout-i-actual-contract-batching.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({'verdict':'PASS','batches':len(phases),'contracts':len(merged),'proposed_criteria':len(ids)},indent=2))
