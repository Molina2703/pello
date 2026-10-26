"""Independent failure diagnosis, not an acceptance or complete-plan review."""
import hashlib,json,sqlite3,sys
from pathlib import Path
from typing import Literal
from pydantic import Field
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.messages import Message
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend
class GraphFailureDiagnosis(Message):
    classification:Literal['planner_output','requirement_interpretation','validator','mixed','uncertain']
    objective_rejection_justified:bool
    critical_findings:list[str]=Field(min_length=1,max_length=8)
    source_consistency_findings:list[str]=Field(min_length=1,max_length=8)
    smallest_generic_remediation:str=Field(max_length=2500)
    implementation_change_justified:bool
    explanation:str=Field(max_length=2500)
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-h-freeze-v2.json').read_text());diagnosis=json.loads((out/'heldout-h-graph-diagnosis.json').read_text());p=json.loads((out/'heldout-h-rejected-architecture.json').read_text())
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');a=json.loads(c.execute("select analysis from pello_product_versions where project_id='phase3c3-heldout-h'").fetchone()[0]);c.close()
packet={'objective':'Independent diagnosis of a preserved genuine held-out planning FAIL, against original source. This is NOT full-plan semantic acceptance and must not override objective FAIL. Determine whether the rejected graph loses a legitimate accepted requirement dependency, whether the interpretation imposed an unjustified prerequisite, or whether validator is incorrect. Assess ordering/grouping of pre-send authorization enforcement versus external delivery and ordinary local approval. Generic remediation only: no replacement architecture, graph or manually assigned nodes. Do not modify implementation. If this is model output violating an already enforced invariant, distinguish that from a demonstrated deterministic code defect; do not propose speculative changes just to obtain PASS. No private Planner reasoning is provided.',
 'original_specification':(out/'heldout-h-spec-v2.md').read_text(),'analysis_requirements':[{k:r[k] for k in ['requirement_id','source_ids','normalized','category','depends_on','uncertainty','authorization_required']} for r in a['requirements']],'analysis_issues':a['issues'],'rejected_architecture':p,'objective_missing_prerequisites':diagnosis,
 'validator_contract':'A node requirement prerequisite must be covered by its own node, an ancestor node or a permitted global constraint. Transitive node ancestors count. All integration requirements need external-operation nodes; global authorization constraints also need local enforcement. No cycles, dropped requirements, invented resources or authorization are permitted.',
 'scope':'H remains original FAIL. No increments/contracts/manifest generated; no business implementation or tests executed. All frozen expectations remain unchanged.'}
(out/'heldout-h-graph-diagnosis-review-input.json').write_text(json.dumps(packet,indent=2,ensure_ascii=False))
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
    result,raw=core._invoke('phase3c3-review-h',1,'heldout-h-graph-failure-diagnosis','reviewer',packet,GraphFailureDiagnosis)
    record={'diagnosis':result.model_dump(mode='json'),'thread_id':raw['thread_id'],'turn_id':raw['turn_id'],'input_sha256':hashlib.sha256((out/'heldout-h-graph-diagnosis-review-input.json').read_bytes()).hexdigest(),'H_verdict_unchanged':'FAIL'}
    (out/'heldout-h-independent-graph-diagnosis.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))
finally:core.backend.close()
