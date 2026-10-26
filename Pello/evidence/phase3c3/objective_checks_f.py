"""Registered before held-out Planner execution; business semantics use frozen rubric."""
import hashlib,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore,MarkdownSource
from athis_autopilot.pipeline import IncrementalPipeline
from athis_autopilot.pipeline_contracts import PipelineManifest

def evaluate():
    out=Path('evidence/phase3c3');f=json.loads((out/'heldout-f-freeze.json').read_text())
    core=ProductPlanningCore(Path('runtime/phase3c'));pid='phase3c3-heldout-f';checks=[]
    def check(name,condition,evidence):
        checks.append({'check':name,'verdict':'PASS' if condition else 'FAIL','evidence':evidence})
    try:
        source=(out/'heldout-f-spec.md').read_bytes();rubric=Path(f['private_rubric_path']).read_bytes()
        check('frozen_source_and_rubric',hashlib.sha256(source).hexdigest()==f['specification_sha256'] and hashlib.sha256(rubric).hexdigest()==f['rubric_sha256'],f['evaluation_id'])
        recovered=core.reconstruct_plan(pid);p=recovered['plan'];a=p['requirements'];arch=p['stages']['architecture'];incs=p['stages']['increments']['proposal']['increments'];contracts=p['stages']['contracts']['proposal']['contracts'];model=p['stages']['models']
        check('traceable_source',p['source_sha256']==f['specification_sha256'] and a['source_segments']==[s.model_dump(mode='json') for s in MarkdownSource.parse(source.decode())],p['source_sha256'])
        required={r['requirement_id'] for r in a['requirements'] if r['category']!='untrusted_instruction'}
        covered=set(arch['proposal']['global_requirement_ids'])|{r for n in arch['proposal']['nodes'] for r in n['requirement_ids']}
        check('mandatory_requirement_coverage',required==covered,{'requirements':len(required),'covered':len(covered)})
        manifest=PipelineManifest.model_validate(p['manifest']);order=[i.task_id for i in manifest.increments];positions={v:i for i,v in enumerate(order)}
        check('existing_manifest_and_dag',len(order)==len(positions)==len(incs) and all(positions[d]<positions[i.task_id] for i in manifest.increments for d in i.depends_on),order)
        issue_blocked={i['task_id'] for i in incs if any(s['severity']=='blocking' and set(s['affected_requirement_ids'])&set(i['requirement_ids']) for s in a['issues'])}
        external={i['task_id'] for i in incs if i['operation_kind']=='external_operation'}
        seen=set();queue=[frozenset()];ever=set();safe=True;states=[]
        while queue:
            completed=queue.pop()
            if completed in seen:continue
            seen.add(completed);r=IncrementalPipeline.inspect_planned_manifest(manifest,completed=completed)
            safe &= not bool(set(r['ready'])&(issue_blocked|external));ever.update(r['ready'])
            states.append({'hypothetically_completed':sorted(completed),'ready':r['ready']})
            queue.extend(completed|{t} for t in r['ready'])
        first=core.inspect_plan(pid)
        check('blocked_and_external_branches_ineligible',safe,{'blocked':sorted(issue_blocked),'external':sorted(external),'reachable_scheduler_states':len(states)})
        check('independent_local_progress',first['first_actionable'] is not None and len(ever)>=2,{'first':first['first_actionable'],'eventually_actionable_without_resolving_blockers':sorted(ever),'states':states})
        check('contract_lifecycle',len(contracts)==len(incs) and all(c['state']=='proposed' for x in contracts for c in x['criteria']) and p['acceptance_lifecycle']=={'criteria':'proposed','tests':'not_generated','protected':False,'executed':False,'observed_results':[]},{'contracts':len(contracts),'proposed_criteria':sum(len(x['criteria']) for x in contracts)})
        records=model['records'];valid=all(r['verified_availability'] and r['selected_reasoning_effort'] in r['capability_snapshot']['models'].get(r['resolved_technical_model_id'],[]) and not r['product_execution_authorized'] for r in records)
        check('typed_catalog_validated_model_assignments',valid and len(records)==len(incs),[{'task':r['task_id'],'model':r['selected_model_profile'],'effort':r['selected_reasoning_effort']} for r in records])
        with core.db() as cx:
            before=cx.execute('select count(*) from pello_product_operations').fetchone()[0]
            history=cx.execute('select count(*) from pello_product_plan_history where project_id=?',(pid,)).fetchone()[0]
        command=[sys.executable,'-B','-m','athis_autopilot','--root','runtime','plan-spec','--inspect-plan','--project-id',pid]
        r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
        (out/'heldout-f-restart.log').write_text(r.stdout+r.stderr)
        cli=json.loads(r.stdout) if r.returncode==0 else {}
        with core.db() as cx:after=cx.execute('select count(*) from pello_product_operations').fetchone()[0]
        check('restart_reconstruction_without_inference',r.returncode==0 and cli.get('plan_sha256')==recovered['plan_sha256'] and before==after and history==1,{'counter_before':before,'counter_after':after,'history_rows':history,'cli':cli})
        check('no_product_implementation_or_authorized_effects',p['execution_authorized'] is False and first['execution_authorized'] is False and not list((core.folder(pid)/'workspace').rglob('*.py')),{'execution_authorized':False,'business_product_tests':'not generated/protected/executed','workspace_python_files':0})
        result={'evaluation_id':f['evaluation_id'],'plan_sha256':recovered['plan_sha256'],'verdict':'PASS' if all(c['verdict']=='PASS' for c in checks) else 'FAIL','checks':checks,'checks_run':len(checks),'checks_passed':sum(c['verdict']=='PASS' for c in checks),'semantic_verdict':'pending independent frozen-rubric review'}
        (out/'heldout-f-objective.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2),flush=True)
        return result
    finally:core.backend.close()

if __name__=='__main__':evaluate()
