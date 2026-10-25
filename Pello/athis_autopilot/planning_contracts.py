"""Planning extensions of Pello's existing contracts; no execution authority."""
from typing import Literal
from pydantic import Field
from .messages import Message, Identifier, Text
from .pipeline_contracts import relative_path
from .pipeline_contracts import Increment,PipelineManifest,ToolBinding,ModelProfile,PipelinePolicy


class WorkNode(Message):
    task_id: Identifier
    objective: Text
    requirement_ids: list[Identifier] = Field(min_length=1,max_length=30)
    depends_on: list[Identifier] = Field(max_length=8)
    optional_dependencies: list[Identifier] = Field(max_length=8)
    required_resources: list[Identifier] = Field(max_length=12,description="Resource identifiers needing separate availability/permission checks, including genuinely missing infrastructure or external services. Do not put provided local Python/SQLite/Git capabilities, supplied synthetic data, source rules, assumptions, or future task outputs here; functional prerequisites belong in depends_on and inputs. Use [] when no such resource prerequisite is missing. With no supplied resource inventory, every listed identifier is treated as unavailable; a declaration is never availability or authorization.")
    operation_kind: Literal['local_logic','external_operation']


class ArchitectureProposal(Message):
    architecture: list[Text] = Field(min_length=1,max_length=12)
    data_entities: list[Text] = Field(min_length=1,max_length=20)
    interfaces: list[Text] = Field(min_length=1,max_length=20)
    operational_constraints: list[Text] = Field(min_length=1,max_length=12)
    security_considerations: list[Text] = Field(min_length=1,max_length=12)
    technical_risks: list[Text] = Field(min_length=1,max_length=12)
    completion_definition: list[Text] = Field(min_length=1,max_length=12)
    global_requirement_ids: list[Identifier] = Field(max_length=30,description="Existing requirement IDs only from categories exclusion, constraint, non_functional or authorization. A functional requirement or business_rule must be assigned to work nodes even when cross-cutting; neither category may be globalized. An authorization global must also map to a local enforcement work node. Do not change requirement categories or use global placement to bypass blockers.")
    nodes: list[WorkNode] = Field(min_length=1,max_length=8)


def validate_architecture(proposal, analysis, *, available_resources=(), completed=()):
    """Stable topological order and blockers; proposed availability is never trusted."""
    from .product_planning import _assert_acyclic
    requirements={r.requirement_id:r for r in analysis.requirements}
    nodes={n.task_id:n for n in proposal.nodes}
    if len(nodes)!=len(proposal.nodes): raise ValueError('Duplicate task ID')
    global_ids=set(proposal.global_requirement_ids)
    if (len(global_ids)!=len(proposal.global_requirement_ids) or not global_ids<=requirements.keys()
            or any(requirements[r].category not in ('exclusion','constraint','non_functional','authorization') for r in global_ids)):
        raise ValueError('Global constraints must refer only to source constraints/exclusions')
    coverage=set(global_ids)
    for node in nodes.values():
        ids=set(node.requirement_ids)
        if len(ids)!=len(node.requirement_ids) or not ids<=requirements.keys(): raise ValueError('Invalid requirement references')
        if any(requirements[r].category=='untrusted_instruction' for r in ids): raise ValueError('Untrusted text cannot become work')
        if len(set(node.depends_on))!=len(node.depends_on): raise ValueError('Duplicate dependency')
        if node.task_id in node.depends_on or not set(node.optional_dependencies)<=nodes.keys() or node.task_id in node.optional_dependencies:
            raise ValueError('Invalid/self dependency')
        if node.operation_kind=='local_logic' and any(requirements[r].category=='integration' for r in ids):
            raise ValueError('An integration requirement cannot be fulfilled only by local logic')
        coverage.update(ids)
    mandatory={r.requirement_id for r in analysis.requirements if r.category!='untrusted_instruction'}
    if coverage!=mandatory: raise ValueError('Mandatory source requirement coverage incomplete')
    for req_id in global_ids:
        if requirements[req_id].category=='authorization' and not any(
                req_id in n.requirement_ids and n.operation_kind=='local_logic' for n in nodes.values()):
            raise ValueError('A global authorization constraint also needs a local enforcement task')
    edges={n.task_id:n.depends_on for n in nodes.values()}
    _assert_acyclic(edges,'Task')
    order=[];remaining=set(nodes)
    while remaining:
        layer=sorted(n for n in remaining if set(edges[n])<=set(order))
        if not layer: raise ValueError('No topological ordering')
        order.extend(layer);remaining.difference_update(layer)
    ancestors={}
    for task_id in order:
        ancestors[task_id]=set(nodes[task_id].depends_on)
        for dep in nodes[task_id].depends_on: ancestors[task_id].update(ancestors[dep])
        covered_before=set(global_ids)|set(nodes[task_id].requirement_ids)
        for dep in ancestors[task_id]:covered_before.update(nodes[dep].requirement_ids)
        for req_id in nodes[task_id].requirement_ids:
            if not set(requirements[req_id].depends_on)<=covered_before:
                raise ValueError('Task graph loses source requirement prerequisites')
    blockers={};ready=[]
    for task_id in order:
        node=nodes[task_id];linked=set(node.requirement_ids)
        causes=['specification:'+i.issue_id for i in analysis.issues
                if i.severity=='blocking' and linked.intersection(i.affected_requirement_ids)]
        causes += ['resource:'+r for r in node.required_resources if r not in available_resources]
        if node.operation_kind=='external_operation': causes.append('authorization')
        causes += ['dependency:'+d for d in node.depends_on if d not in completed]
        blockers[task_id]=sorted(set(causes))
        if not causes and task_id not in completed:ready.append(task_id)
    return {'order':order,'blockers':blockers,'ready':ready,'completed':sorted(set(completed)&nodes.keys()),
            'coverage':sorted(coverage),'execution_authorized':False}


class FunctionalIncrement(WorkNode):
    inputs: list[Text] = Field(min_length=1,max_length=12)
    outputs: list[Text] = Field(min_length=1,max_length=12)
    interfaces: list[Text] = Field(min_length=1,max_length=12)
    components: list[Text] = Field(min_length=1,max_length=12)
    tools: list[Identifier] = Field(min_length=1,max_length=12)
    permissions: list[Text] = Field(max_length=12)
    external_effects: list[Text] = Field(max_length=12)
    completion_conditions: list[Text] = Field(min_length=1,max_length=12)
    verification_evidence: list[Text] = Field(min_length=1,max_length=12)
    boundary_rationale: Text


class FunctionalIncrements(Message):
    increments: list[FunctionalIncrement] = Field(min_length=1,max_length=8)


def validate_increments(decomposition, architecture, analysis, *, completed=()):
    graph=validate_architecture(architecture,analysis,completed=completed)
    expected={n.task_id:n for n in architecture.nodes}
    actual={n.task_id:n for n in decomposition.increments}
    if actual.keys()!=expected.keys() or len(actual)!=len(decomposition.increments):
        raise ValueError('Increment coverage/identity differs from the validated graph')
    for key,inc in actual.items():
        if inc.model_dump(include=set(WorkNode.model_fields))!=expected[key].model_dump():
            raise ValueError('Increment silently changes architecture, references or dependencies')
        for component in inc.components: relative_path(component)
        if not set(inc.tools)<={'python','git','external_api','n8n'}:
            raise ValueError('Unknown tool capability: use the explicit project planning catalog')
        if inc.operation_kind=='external_operation' and (not inc.permissions or not inc.external_effects):
            raise ValueError('External operations require explicit effects and permission requirements')
        if inc.operation_kind=='local_logic' and inc.external_effects:
            raise ValueError('Local logic cannot declare external operations')
    states={}
    for key in graph['order']:
        causes=graph['blockers'][key]
        states[key]=('completed' if key in completed else 'specification_blocked' if any(c.startswith('specification:') for c in causes)
            else 'authorization_blocked' if 'authorization' in causes else 'resource_blocked' if any(c.startswith('resource:') for c in causes)
            else 'dependency_blocked' if causes else 'ready')
    return {**graph,'states':states,'first_actionable':next(iter(graph['ready']),None),
        'readiness_meaning':'Ready to prepare protected tests and request execution authorization, not permission to run a Coder.'}


class AcceptanceCriterion(Message):
    criterion_id: Identifier
    requirement_ids: list[Identifier] = Field(min_length=1,max_length=30)
    kind: Literal['normal','invalid','boundary','error','permission','regression','external']
    given: Text
    action: Text
    expected: Text
    verification: Literal['deterministic_local','external_execution','inspection']
    state: Literal['proposed']


class TechnicalContract(Message):
    task_id: Identifier
    preconditions: list[Text] = Field(min_length=1,max_length=12)
    data_structures: list[Text] = Field(min_length=1,max_length=12)
    business_rules: list[Text] = Field(min_length=1,max_length=12)
    validation_behavior: list[Text] = Field(min_length=1,max_length=12)
    error_behavior: list[Text] = Field(min_length=1,max_length=12)
    criteria: list[AcceptanceCriterion] = Field(min_length=3,max_length=20)
    unresolved_issue_ids: list[Identifier] = Field(max_length=30)


class IncrementContracts(Message):
    contracts: list[TechnicalContract] = Field(min_length=1,max_length=8)


def validate_contracts(contracts,decomposition,architecture,analysis):
    readiness=validate_increments(decomposition,architecture,analysis)
    increments={x.task_id:x for x in decomposition.increments}
    if {c.task_id for c in contracts.contracts}!=increments.keys() or len(contracts.contracts)!=len(increments):
        raise ValueError('Contracts must cover each increment exactly once')
    issues={i.issue_id for i in analysis.issues};all_criteria=set();count=0
    for contract in contracts.contracts:
        allowed=set(increments[contract.task_id].requirement_ids)|set(architecture.global_requirement_ids)
        coverage=set();kinds=set()
        if not set(contract.unresolved_issue_ids)<=issues: raise ValueError('Unknown unresolved issue')
        for criterion in contract.criteria:
            if criterion.criterion_id in all_criteria:raise ValueError('Duplicate acceptance criterion ID')
            all_criteria.add(criterion.criterion_id);count+=1;kinds.add(criterion.kind)
            if not set(criterion.requirement_ids)<=allowed: raise ValueError('Criterion requirement lies outside its contract')
            coverage.update(criterion.requirement_ids)
        if coverage!=allowed: raise ValueError('Missing requirement or global exclusion acceptance coverage')
        if not {'normal','invalid','boundary'}<=kinds:raise ValueError('Normal/invalid/boundary acceptance coverage required')
        if increments[contract.task_id].operation_kind=='external_operation' and 'permission' not in kinds:
            raise ValueError('External operations require permission acceptance criteria')
    return {'criteria_count':count,'contract_count':len(contracts.contracts),'test_lifecycle':'not_generated',
        'tests_protected':False,'tests_executed':False,'observed_results':[],
        'external_verification_required':[i.task_id for i in decomposition.increments if i.operation_kind=='external_operation'],
        'readiness':readiness}


def manifest_from_contracts(contracts,decomposition,architecture,analysis):
    import json
    validation=validate_contracts(contracts,decomposition,architecture,analysis)
    incs={i.task_id:i for i in decomposition.increments};cs={c.task_id:c for c in contracts.contracts}
    tasks=[]
    for key in validation['readiness']['order']:
        i,c=incs[key],cs[key]
        tasks.append(Increment(task_id=key,specification=i.objective+'\nContract: '+json.dumps(c.model_dump(mode='json',exclude={'criteria'}),ensure_ascii=False),
            inputs=i.inputs,outputs=i.outputs,components=i.components,
            acceptance_criteria=[f'{x.criterion_id}: Given {x.given}; when {x.action}; expect {x.expected}' for x in c.criteria],
            depends_on=i.depends_on,suite='planned/'+key,expected_tests=len(c.criteria),risk='high' if i.operation_kind=='external_operation' else 'routine'))
    tools=[]
    for tool in sorted({t for i in incs.values() for t in i.tools}):
        tools.append(ToolBinding(tool=tool,environment='local' if tool in ('python','git') else 'production',
            connection_ref='',allowed_operations=['implement','run_tests'] if tool=='python' else ['inspect','checkpoint'] if tool=='git' else [],
            resource_ids=[],verification='Proposed capability only; independent protected tests and execution authorization remain required.',
            enabled=tool in ('python','git')))
    return PipelineManifest(architecture_constraints=architecture.operational_constraints,tools=tools,increments=tasks)


class FailureEvidence(Message):
    category: Literal['implementation','contract','integration','infrastructure','reasoning']
    severity: Literal['minor','major','critical']
    localized: bool
    meaningful_progress: bool
    actionable_diagnosis: bool
    persistent_capability_gap: bool
    recommendation: Literal['continue','replan','escalate']
    evidence_refs: list[Text] = Field(min_length=1,max_length=12)


class ModelDecisionProposal(Message):
    task_id: Identifier
    responsibility: Literal['coder']
    profile: ModelProfile
    complexity: Literal['simple','normal','complex']
    risk: Literal['low','medium','high','critical']
    uncertainty: Literal['low','medium','high']
    context_requirements: Literal['small','medium','large']
    expected_turns: int = Field(ge=1,le=12)
    selection_kind: Literal['initial','adaptation']
    previous_configuration: ModelProfile | None
    failure_evidence: FailureEvidence | None
    exceptional_initial_sol: bool
    decomposition_considered: bool
    evidence_refs: list[Text] = Field(min_length=1,max_length=12)
    rationale: Text


class TaskModelAssignments(Message):
    decisions: list[ModelDecisionProposal] = Field(min_length=1,max_length=8)


def validate_model_decision(proposal,capabilities,*,budget_remaining):
    from .engines import CodexBlocked
    from .model_policy import select_model
    from .supervisor import now
    if budget_remaining<proposal.expected_turns:
        raise CodexBlocked('Insufficient bounded model capacity for the proposed decision')
    sol=proposal.profile.model!='gpt-6-luna'
    if proposal.selection_kind=='initial':
        if proposal.previous_configuration or proposal.failure_evidence:
            raise ValueError('Initial model choice must not invent a prior attempt')
        if sol and not (proposal.exceptional_initial_sol and (proposal.risk=='critical' or
                (proposal.complexity=='complex' and proposal.risk=='high'))):
            raise ValueError('Initial Sol needs exceptional complexity/risk evidence')
    else:
        previous,failure=proposal.previous_configuration,proposal.failure_evidence
        if previous is None or failure is None:raise ValueError('Adaptation requires previous profile and typed review evidence')
        if sol and previous.model=='gpt-6-luna':
            justified=(failure.severity=='critical' or
                (failure.persistent_capability_gap and not failure.meaningful_progress))
            if not justified or failure.recommendation!='escalate':
                raise ValueError('Ordinary localized failures/progress do not justify automatic Sol escalation')
    # Exact Planner profile: risk and retry counters must not override a justified Luna High choice.
    policy=PipelinePolicy(role_profiles={'coder':proposal.profile})
    selected=select_model(policy,capabilities,phase='planned-implementation',responsibility='coder')
    return {'task_id':proposal.task_id,'logical_responsibility':proposal.responsibility,
        'decision_timestamp':now(),'selected_model_profile':proposal.profile.model,
        'selected_reasoning_effort':proposal.profile.effort,'resolved_technical_model_id':selected['model'],
        'verified_availability':True,'capability_snapshot':capabilities,
        'complexity':proposal.complexity,'risk':proposal.risk,'context_requirements':proposal.context_requirements,
        'budget_assessment':{'remaining_development_turns':budget_remaining,'estimated_coder_turns':proposal.expected_turns,
            'product_execution_budget':'not_authorized_or_reserved'},
        'selection_kind':proposal.selection_kind,'previous_configuration':proposal.previous_configuration.model_dump() if proposal.previous_configuration else None,
        'is_escalation':bool(sol and proposal.previous_configuration and proposal.previous_configuration.model=='gpt-6-luna'),
        'evidence_refs':proposal.evidence_refs,'justification':proposal.rationale,'proposal':proposal.model_dump(mode='json'),
        'product_execution_authorized':False}


class CapabilityProbe(Message):
    item_count: int = Field(ge=0,le=10)


def model_budget_summary(records):
    estimated=sum(r['budget_assessment']['estimated_coder_turns'] for r in records)
    capacity=min(r['budget_assessment']['remaining_development_turns'] for r in records)
    return {'estimated_coder_turns_total':estimated,'development_capacity_at_decision':capacity,
        'shortfall':max(0,estimated-capacity),'combined_estimate_fits_development_capacity':estimated<=capacity,
        'product_execution_authorized':False,'product_execution_budget':'not_granted',
        'scope':'Estimates are proposals, not reservations. Individual eligibility never proves aggregate execution feasibility.'}
