"""Reproduce every frozen deny root; no model inference or rubric changes."""
import json,sqlite3,subprocess,sys
from pathlib import Path
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-g-freeze.json').read_text())
roots=[Path(p) for p in f['deny_read_roots']]
profile='{extends=":read-only",filesystem={'+','.join(json.dumps(p.as_posix())+'="deny"' for p in roots)+'},network={enabled=false}}'
cli=Path('.venv/Lib/site-packages/codex_cli_bin/bin/codex.exe').resolve()
prefix=[str(cli),'-c','permissions.pello_supplied_context='+profile,'sandbox','-P','pello_supplied_context']
checks=[]
public=Path('runtime/phase3c/projects/phase3c3-isolation-review/workspace/public-canary.txt').resolve()
for index,path in enumerate([public]+roots):
    allowed=index==0
    program='from pathlib import Path; import sys; p=Path(sys.argv[1]); list(p.iterdir()) if p.is_dir() else p.read_bytes(); print("READ_SUCCEEDED")'
    command=prefix+[sys.executable,'-B','-c',program,str(path)]
    r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
    passed=r.returncode==0 if allowed else r.returncode!=0 and 'PermissionError' in r.stderr
    checks.append({'path':str(path),'expected_read':allowed,'exit_code':r.returncode,'passed':passed,'stdout':r.stdout,'stderr':r.stderr,'command':command})
    assert passed,checks[-1]
query='SELECT count(*) FROM pello_product_projects WHERE project_id=?';bindings=['phase3c3-heldout-g']
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');observed=c.execute(query,bindings).fetchone()[0];c.close();assert observed==0
receipt=Path('runtime/phase3c/projects/phase3c3-author/evidence/version-1/author-heldout-g/model-turn-submitted.json')
record={'native_checks':checks,'Planner_absence':{'executed_sql':query,'bindings':bindings,'observed_count':observed},'complete_profile_runtime_receipt':json.loads(receipt.read_text()),'freeze_unchanged':True}
(out/'full-boundary-g-objective.json').write_text(json.dumps(record,indent=2));print(json.dumps({'native_checks':len(checks),'pass':all(x['passed'] for x in checks),'Planner_rows':observed}),flush=True)
