"""One explicit reconciled provider retry, retaining both charges and all evidence.

No implementation, policy, source, rubric, technical plan or counters are changed.
The original submitted turn is proven terminal failed, with no assistant output.
"""
import hashlib,json,sqlite3,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore,validate_planning_input
from athis_autopilot.planning_contracts import ArchitectureProposal,validate_architecture
from athis_autopilot.ai_supervisor import SDKBackend
out=Path('evidence/phase3c3');pid='phase3c3-heldout-e';original='plan-architecture'
proof=json.loads((out/'sdk-provider-block-reconciliation.json').read_text())
failed=proof['turns'][-1]
assert failed['status']=='failed' and failed['error']['codex_error_info']=='usageLimitExceeded'
assert proof['last_turn_item_types']==['userMessage']
limits=proof['rate_limits'];bucket=limits['rateLimitsByLimitId']['codex']
assert limits['ordinaryUsageAllowed'] and bucket['primary']['usedPercent']<90 and bucket['secondary']['usedPercent']<90
f=json.loads((out/'heldout-e-freeze.json').read_text())
assert hashlib.sha256((out/'heldout-e-spec.md').read_bytes()).hexdigest()==f['specification_sha256']
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=f['deny_read_roots']),timeout=600)
try:
 directory=core.folder(pid)/'evidence/version-1'/original
 assert not (directory/'codex_result.json').exists()
 payload=json.loads((directory/'input.json').read_text(encoding='utf-8'))
 with core.db() as c:
  before=c.execute('select count(*) from pello_product_operations').fetchone()[0]
  row=dict(c.execute('select * from pello_product_operations where project_id=? and version=1 and phase=?',(pid,original)).fetchone())
  assert row['status']=='IN_FLIGHT'
  assert hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True).encode()).hexdigest()==json.loads(row['request'])['input_sha256']
  (out/'provider-recovery-original-operation.json').write_text(json.dumps(row,indent=2),encoding='utf-8')
  response={'reconciliation':'TERMINAL_PROVIDER_QUOTA_FAILURE','failed_thread_turn':failed,'thread_id':json.loads((directory/'model-turn-submitted.json').read_text())['thread_id'],'no_assistant_output':True,'retained_charge':True,'proof':'sdk-provider-failed-thread.json'}
  c.execute("update pello_product_operations set status='FAILED_PROVIDER_QUOTA_RECONCILED',response=?,modified=? where project_id=? and version=1 and phase=? and status='IN_FLIGHT'",(json.dumps(response),datetime.now(timezone.utc).isoformat(),pid,original))
  assert c.execute('select count(*) from pello_product_operations').fetchone()[0]==before
 (out/'provider-recovery-authorization-check.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'prior_charges':before,'limit':75,'deadline':'2026-10-26T03:30:00+00:00','explicit_grant':'authorization-extension-75.json','new_attempts_allowed_by_this_harness':1,'same_payload_and_schema':True,'same_model_policy':True,'no_counter_reset':True,'terminal_failure_proven':response,'provider_read_reports_available':True},indent=2),encoding='utf-8')
 draft,raw=core._invoke(pid,1,'plan-architecture-provider-recovery-1','planner',payload,ArchitectureProposal)
 result={'proposal':draft.model_dump(mode='json'),'validation':validate_architecture(draft,validate_planning_input(payload['requirements']))}
 core._ensure_json_artifact(core.folder(pid)/'evidence/version-1/planning/architecture.json',result)
 # Resume ordinary existing pipeline; no manual design, increment or contract.
 plan=core.plan_product(pid)
 (out/'heldout-e-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
 (out/'heldout-e-pipeline-inspection.json').write_text(json.dumps(core.inspect_plan(pid),indent=2),encoding='utf-8')
 status={'status':'PLANNING_COMPLETED_PENDING_INDEPENDENT_EVALUATION','plan_sha256':plan['plan_sha256'],'project_id':pid,'sdk_turns':core.project_row(pid)['used_turns'],'provider_failure_charge_retained':True,'at':datetime.now(timezone.utc).isoformat()}
 (out/'heldout-e-recovered-run-status.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status,indent=2),flush=True)
finally:core.backend.close()
