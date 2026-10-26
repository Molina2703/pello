"""Read-only provider accounting/turn reconciliation; never submits inference."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from pydantic import BaseModel,ConfigDict
from openai_codex import Codex,CodexConfig
from athis_autopilot.codex_worker import restricted_overrides
class Raw(BaseModel):model_config=ConfigDict(extra='allow')
out=Path('evidence/phase3c3');folder=Path('runtime/phase3c/projects/phase3c3-heldout-e')
with Codex(CodexConfig(config_overrides=restricted_overrides())) as client:
 limits=client._client.request('account/rateLimits/read',{},response_model=Raw).model_dump(mode='json')
 (out/'sdk-provider-rate-limits.json').write_text(json.dumps(limits,indent=2),encoding='utf-8')
 thread=client._client.thread_read((folder/'planner-thread.txt').read_text().strip(),include_turns=True).model_dump(mode='json')
 (out/'sdk-provider-failed-thread.json').write_text(json.dumps(thread,indent=2),encoding='utf-8')
 turns=thread['thread']['turns'];summaries=[{k:t.get(k) for k in ('id','status','error')} for t in turns]
 state={'at':datetime.now(timezone.utc).isoformat(),'rate_limits':limits,'turns':summaries,'last_turn_item_types':[x.get('type') for x in turns[-1].get('items',[])] if turns else [],'inference_submitted_by_this_script':False}
 (out/'sdk-provider-block-reconciliation.json').write_text(json.dumps(state,indent=2),encoding='utf-8');print(json.dumps(state,indent=2))
