"""Real existing C1 -> C2 pipeline; no technical plan is provided here."""
import hashlib,json,sys,traceback
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.ai_supervisor import SDKBackend

out=Path('evidence/phase3c3');freeze=json.loads((out/'heldout-g-freeze-v2.json').read_text())
assert json.loads((out/'heldout-g-preparation-accepted-v2.json').read_text())['status']=='ACCEPTED'
assert hashlib.sha256((out/'heldout-g-spec.md').read_bytes()).hexdigest()==freeze['specification_sha256']
assert hashlib.sha256(Path(freeze['private_rubric_path']).read_bytes()).hexdigest()==freeze['rubric_sha256']
core=ProductPlanningCore(Path('runtime/phase3c'),backend=SDKBackend(denied_read_roots=freeze['deny_read_roots']),timeout=600)
pid='phase3c3-heldout-g'
try:
    try:core.project_row(pid)
    except ValueError:
        remaining=int((datetime.fromisoformat('2026-10-27T06:30:00+00:00')-datetime.now(timezone.utc)).total_seconds()//60)
        core.create_project(out/'heldout-g-spec.md',project_id=pid,duration_minutes=min(330,remaining))
    result=core.plan_product(pid)
    (out/'heldout-g-plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
    (out/'heldout-g-pipeline-inspection.json').write_text(json.dumps(core.inspect_plan(pid),indent=2))
    status={'status':'PLANNING_COMPLETED_PENDING_INDEPENDENT_EVALUATION','plan_sha256':result['plan_sha256'],'project_id':pid,'sdk_turns':core.project_row(pid)['used_turns'],'at':datetime.now(timezone.utc).isoformat()}
except Exception as exc:
    status={'status':'FAIL_OR_BLOCKED','error_type':type(exc).__name__,'error':str(exc),'project_id':pid,'at':datetime.now(timezone.utc).isoformat()}
    traceback.print_exc()
finally:
    (out/'heldout-g-run-status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2),flush=True)
    core.backend.close()
