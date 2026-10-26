"""Same-payload retry after terminal reconciliation and explicit renewed deadline.
Uses existing reservation/submission gates and unchanged validators. No design is
supplied by the harness, no prior operation is replaced and no charge is reset.
"""
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore,validate_planning_input
from athis_autopilot.planning_contracts import ArchitectureProposal,validate_architecture
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3');pid='phase3c3-heldout-e'
grant=json.loads((out/'authorization-deadline-0630.json').read_text());assert datetime.now(timezone.utc)<datetime.fromisoformat(grant['deadline'])
f=json.loads((out/'heldout-e-freeze.json').read_text());assert hashlib.sha256((out/'heldout-e-spec.md').read_bytes()).hexdigest()==f['specification_sha256']
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
 with core.db() as c:
  old=dict(c.execute("select * from pello_product_operations where project_id=? and phase='plan-architecture'",(pid,)).fetchone())
  auth=dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone())
 assert old['status']=='FAILED_PROVIDER_QUOTA_RECONCILED'
 assert json.loads(old['response'])['no_assistant_output'] is True
 assert auth['id']==grant['id'] and auth['deadline']==grant['deadline'] and auth['max_turns']==75
 core._budget_check(core.project_row(pid))
 original=core.folder(pid)/'evidence/version-1/plan-architecture'
 payload=json.loads((original/'input.json').read_text(encoding='utf-8'))
 assert hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()==json.loads(old['request'])['input_sha256']
 assert hashlib.sha256(json.dumps(ArchitectureProposal.model_json_schema(),ensure_ascii=False,sort_keys=True).encode()).hexdigest()==json.loads(old['request'])['schema_sha256']
 receipt={'at':datetime.now(timezone.utc).isoformat(),'grant_id':grant['id'],'same_input_sha256':json.loads(old['request'])['input_sha256'],'same_schema_sha256':json.loads(old['request'])['schema_sha256'],'original_terminal_failure_preserved':True,'original_charge_retained':True,'new_attempts':1,'deadline':auth['deadline'],'maximum':auth['max_turns']}
 (out/'provider-recovery-renewed-authorization.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
 draft,raw=core._invoke(pid,1,'plan-architecture-provider-recovery-1','planner',payload,ArchitectureProposal)
 result={'proposal':draft.model_dump(mode='json'),'validation':validate_architecture(draft,validate_planning_input(payload['requirements']))}
 core._ensure_json_artifact(core.folder(pid)/'evidence/version-1/planning/architecture.json',result)
 plan=core.plan_product(pid)
 (out/'heldout-e-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'heldout-e-pipeline-inspection.json').write_text(json.dumps(core.inspect_plan(pid),indent=2),encoding='utf-8')
 status={'status':'PLANNING_COMPLETED_PENDING_INDEPENDENT_EVALUATION','plan_sha256':plan['plan_sha256'],'project_id':pid,'sdk_turns':core.project_row(pid)['used_turns'],'provider_failure_charge_retained':True,'at':datetime.now(timezone.utc).isoformat()}
 (out/'heldout-e-recovered-run-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2),flush=True)
finally:core.backend.close()
