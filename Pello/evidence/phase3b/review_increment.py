"""Independent SDK review of one engineering increment, no MCP or write tools."""
import hashlib
import json
from pathlib import Path
import sys

from athis_autopilot.ai_supervisor import SDKBackend, ROLE_INSTRUCTIONS
from athis_autopilot.messages import parse_response
from athis_autopilot.model_policy import probe_capabilities, select_model
from athis_autopilot.pipeline_contracts import IncrementReview, PipelinePolicy

phase, input_file = sys.argv[1:]
project = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent / 'reviews' / phase
out.mkdir(parents=True, exist_ok=False)
data = json.loads(Path(input_file).read_text(encoding='utf-8'))
for key in ('regression_log', 'baseline_log_tail'):
    log = data.get('verification', {}).get(key)
    if log is not None and not log.rstrip().endswith('OK'):
        raise ValueError('Independent closeout review requires completed regression evidence')
selection = select_model(PipelinePolicy(), probe_capabilities(), phase=phase+'/review')
source = {name:(project / name).read_text(encoding='utf-8') for name in data.pop('source_files')}
hashes = {name:hashlib.sha256((project / name).read_bytes()).hexdigest() for name in source}
context = {'project_id':'phase3b', 'task_id':phase, 'attempt':1, 'objective_evidence':data, 'source':source}
prompt = ('Independently review this bounded engineering increment against its supplied contract and objective evidence. '
    'Return the required verdict. Identify real blocking defects; do not treat deferred future-phase work as a defect. '
    'No tools or file changes. This is review, not implementation.\n' + json.dumps(context))
backend=SDKBackend()
try:
    raw=backend.run(workspace=project, thread_file=out/'reviewer-thread.txt',out_dir=out,role='reviewer',
        model=selection['model'],effort=selection['effort'],prompt=prompt,schema=IncrementReview.model_json_schema(),
        timeout=240,session_db=None,project_id=None,task_id=None)
    review=parse_response(IncrementReview,raw['final_response'])
    assert (review.project_id,review.task_id,review.attempt)==('phase3b',phase,1)
    assert hashes=={name:hashlib.sha256((project/name).read_bytes()).hexdigest() for name in source}
    result={'review':review.model_dump(),'selection':selection,'thread_id':raw['thread_id'],'turn_id':raw['turn_id'],
            'source_sha256':hashes,'evidence_class':'REAL CODEX SDK REVIEW'}
    (out/'review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if review.verdict!='PASS': raise SystemExit(2)
finally:
    backend.close()
