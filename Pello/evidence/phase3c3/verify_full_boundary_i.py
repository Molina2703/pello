"""Reproduce native denial for every root and both private-key aliases."""
import hashlib,json,sqlite3,subprocess,sys
from pathlib import Path
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-i-freeze.json').read_text())
roots=[Path(p) for p in f['deny_read_roots']]
profile='{extends=":read-only",filesystem={'+','.join(json.dumps(p.as_posix())+'="deny"' for p in roots)+'},network={enabled=false}}'
cli=Path('.venv/Lib/site-packages/codex_cli_bin/bin/codex.exe').resolve()
prefix=[str(cli),'-c','permissions.pello_supplied_context='+profile,'sandbox','-P','pello_supplied_context']
public=Path('runtime/phase3c/projects/phase3c3-isolation-review/workspace/public-canary.txt').resolve()
program='from pathlib import Path; import sys; p=Path(sys.argv[1]); list(p.iterdir()) if p.is_dir() else p.read_bytes(); print("READ_SUCCEEDED")'
checks=[]
for index,path in enumerate([public]+roots):
    command=prefix+[sys.executable,'-B','-c',program,str(path)]
    r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
    passed=r.returncode==0 if index==0 else r.returncode!=0 and 'PermissionError' in r.stderr
    checks.append({'path':str(path),'expected_read':index==0,'exit_code':r.returncode,'passed':passed,'stdout':r.stdout,'stderr':r.stderr,'command':command})
    assert passed,checks[-1]
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3')
query='SELECT count(*) FROM pello_product_projects WHERE project_id=?';bindings=['phase3c3-heldout-i']
observed=c.execute(query,bindings).fetchone()[0];c.close();assert observed==0
receipt=Path('runtime/phase3c/projects/phase3c3-author/evidence/version-1/author-heldout-i/model-turn-submitted.json')
record={'native_checks':checks,'Planner_absence':{'executed_sql':query,'bindings':bindings,'observed_count':observed},'complete_profile_runtime_receipt':json.loads(receipt.read_text()),'freeze_unchanged':True}
(out/'full-boundary-i-objective.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
declared=Path(f['private_rubric_path']);canonical=declared.resolve()
alias=Path('C:/Users/USUARIO/AppData/Local/PelloEvaluation/phase3c3-i/rubric.json')
assert declared.samefile(alias)
proof={'declared_path':str(declared),'canonical_path':str(canonical),'normal_alias_path':str(alias),'parent_process_same_file':declared.samefile(canonical),'normal_alias_same_file':True,'declared_sha256':hashlib.sha256(declared.read_bytes()).hexdigest(),'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest(),'frozen_expected_sha256':f['rubric_sha256'],'native_checks':[],'rubric_or_specification_modified':False}
assert proof['declared_sha256']==proof['canonical_sha256']==f['rubric_sha256']
read_program='from pathlib import Path; import sys; Path(sys.argv[1]).read_bytes(); print("READ_SUCCEEDED")'
for label,path in [('declared_rubric_path',declared),('normal_user_alias_path',alias)]:
    command=prefix+[sys.executable,'-B','-c',read_program,str(path)]
    r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
    denied=r.returncode!=0 and 'PermissionError' in r.stderr
    proof['native_checks'].append({'path_label':label,'path':str(path),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'denied':denied,'command':command})
    assert denied
(out/'rubric-i-alias-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
print(json.dumps({'native_root_checks':len(checks),'alias_checks':2,'PASS':True,'Planner_rows':observed}),flush=True)
