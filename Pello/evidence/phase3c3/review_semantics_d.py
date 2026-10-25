"""Independent original-source + frozen-rubric review, never Planner reasoning."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
from evaluation_models import HeldOutFixture,SemanticVerdict
from pack_review import pack_review

out=Path('evidence/phase3c3');f=json.loads((out/'heldout-d-freeze.json').read_text())
rubric=Path(f['private_rubric_path']).read_bytes();assert hashlib.sha256(rubric).hexdigest()==f['rubric_sha256']
fixture=HeldOutFixture.model_validate_json(rubric);obj=json.loads((out/'heldout-d-objective.json').read_text())
p=json.loads((out/'heldout-d-plan.json').read_text())['plan'];a=p['requirements'];st=p['stages']
analysis={k:v for k,v in a.items() if k!='source_segments'}
analysis['source_map']=[{k:v for k,v in s.items() if k!='text'} for s in a['source_segments']]
model_records=[{k:r[k] for k in ('task_id','selected_model_profile','selected_reasoning_effort','resolved_technical_model_id','verified_availability','complexity','risk','context_requirements','budget_assessment','selection_kind','previous_configuration','is_escalation','evidence_refs','justification','proposal','product_execution_authorized')} for r in st['models']['records']]
refs={r['requirement_id'] for r in a['requirements']}|{s['source_id'] for s in a['source_segments']}|{s['issue_id'] for s in a['issues']}|{s['assumption_id'] for s in a['assumptions']}
refs|={n['task_id'] for n in st['increments']['proposal']['increments']}
refs|={c['criterion_id'] for x in st['contracts']['proposal']['contracts'] for c in x['criteria']}
refs|={x['check'] for x in obj['checks']}
refs|={'architecture','dependency_graph','increment_contracts','model_decisions','pipeline_manifest','acceptance_lifecycle'}
packet={'objective':'Independently evaluate Pello autonomous planning against the ORIGINAL unfamiliar business specification and exact frozen rubric. A schema-valid output is insufficient. Check every mandatory business detail, numeric examples, exclusions, drought contradiction, narrow blocker scope, local independent work, atomic reservation/version/reconciliation semantics, permissions and exact-version external authorization. Assess proposed architecture/contracts/criteria, not implemented business product: no Coder or product tests are executed. Do not impose one particular architecture. For each rubric criterion return PASS/FAIL/BLOCKED with supplied evidence IDs. A mandatory objective FAIL cannot be overridden. All critical criteria must pass and at least 90% total must pass. No private Planner conversation/reasoning is supplied. Do not modify anything or use tools. Preserve real semantic defects; do not rationalize them away.',
        'evaluation_id':f['evaluation_id'],'original_specification':fixture.specification_markdown,
        'frozen_rubric':[c.model_dump(mode='json') for c in fixture.rubric],
        'interpretation':analysis,'architecture':st['architecture']['proposal'],
        'dependency_graph':st['architecture']['validation'],'functional_increments':st['increments']['proposal'],
        'increment_contracts':st['contracts']['proposal'],
        'model_decisions':model_records,'actual_catalog':st['models']['records'][0]['capability_snapshot'],
        'aggregate_budget':st['models']['aggregate_budget_assessment'],
        'pipeline_manifest':{'validation':'Existing PipelineManifest accepted, exact full manifest persisted',
            'increments':[{k:v for k,v in i.items() if k not in ('specification','acceptance_criteria','inputs','outputs','components')} for i in p['manifest']['increments']],
            'tool_catalog':p['manifest'].get('tools',[])},
        'acceptance_lifecycle':p['acceptance_lifecycle'],'objective_results':obj,
        'valid_evidence_refs':sorted(refs),'evidence_instruction':'Use exact labels/IDs from valid_evidence_refs, not invented paths. Full original/stage artifacts remain available in durable evidence; this packet removes repeated source text, repeated catalogs and duplicate manifest contract prose only.'}
encoded=json.dumps(packet,ensure_ascii=False,separators=(',',':'))
(out/'heldout-d-semantic-input.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2))
original_length=len(encoded)
packet,aliases=pack_review(packet)
encoded=json.dumps(packet,ensure_ascii=False,separators=(',',':'))
(out/'heldout-d-semantic-packed-input.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2))
(out/'heldout-d-review-packing.json').write_text(json.dumps({'original_characters':original_length,'packed_characters':len(encoded),'exact_round_trip_equal':True,'alias_count':len(aliases),'rubric_expectations_changed':False},indent=2))
print('semantic_packet_characters',original_length,'packed',len(encoded),flush=True)
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    review,raw=core._invoke('phase3c3-review-d',1,'heldout-d-semantic-review','reviewer',packet,SemanticVerdict)
    result=review.model_dump(mode='json')
    for criterion in result['criteria']:
        criterion['evidence_references']=[aliases.get(x,x) for x in criterion['evidence_references']]
    review=SemanticVerdict.model_validate(result)
    (out/'heldout-d-semantic-review.json').write_text(json.dumps(result,indent=2))
    expected={c.criterion_id:c for c in fixture.rubric};observed={c.criterion_id:c for c in review.criteria}
    identity=len(review.criteria)==len(observed) and observed.keys()==expected.keys()
    citations=all(ref in refs for r in review.criteria for ref in r.evidence_references)
    critical=identity and all(observed[k].verdict=='PASS' for k,c in expected.items() if c.severity=='critical')
    fraction=sum(r.verdict=='PASS' for r in review.criteria)/len(expected)
    passed=identity and citations and critical and fraction>=0.9 and not review.critical_failures and review.verdict=='PASS' and obj['verdict']=='PASS'
    evaluation={'evaluation_id':f['evaluation_id'],'plan_sha256':obj['plan_sha256'],'verdict':'PASS' if passed else 'FAIL' if review.verdict!='BLOCKED' else 'BLOCKED',
        'objective_verdict':obj['verdict'],'reviewer_verdict':review.verdict,'criterion_identity_valid':identity,'citation_ids_valid':citations,
        'all_critical_pass':critical,'total_pass_fraction':fraction,'review_thread_id':raw['thread_id'],'review_turn_id':raw['turn_id'],
        'specification_sha256':f['specification_sha256'],'rubric_sha256':f['rubric_sha256'],'no_product_implementation':True}
    (out/'heldout-d-evaluation.json').write_text(json.dumps(evaluation,indent=2));print(json.dumps(evaluation,indent=2),flush=True)
finally:core.backend.close()
