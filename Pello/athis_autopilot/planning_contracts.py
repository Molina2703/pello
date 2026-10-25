"""Planning extensions of Pello's existing contracts; no execution authority."""
from typing import Literal
from pydantic import Field
from .messages import Message, Identifier, Text
from .pipeline_contracts import relative_path
from .pipeline_contracts import Increment,PipelineManifest,ToolBinding


class WorkNode(Message):
    task_id: Identifier
    objective: Text
    requirement_ids: list[Identifier] = Field(min_length=1,max_length=30)
    depends_on: list[Identifier] = Field(max_length=8)
    optional_dependencies: list[Identifier] = Field(max_length=8)
    required_resources: list[Identifier] = Field(max_length=12)
    operation_kind: Literal['local_logic','external_operation']


class ArchitectureProposal(Message):
    architecture: list[Text] = Field(min_length=1,max_length=12)
    data_entities: list[Text] = Field(min_length=1,max_length=20)
    interfaces: list[Text] = Field(min_length=1,max_length=20)
    operational_constraints: list[Text] = Field(min_length=1,max_length=12)
    security_considerations: list[Text] = Field(min_length=1,max_length=12)
    technical_risks: list[Text] = Field(min_length=1,max_length=12)
    completion_definition: list[Text] = Field(min_length=1,max_length=12)
    global_requirement_ids: list[Identifier] = Field(max_length=30)
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
