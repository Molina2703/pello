"""Prove exact frozen key denial, including Windows app-container redirection."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
out=Path('evidence/phase3c3');f=json.loads((out/'heldout-c-freeze.json').read_text())
declared=Path(f['private_rubric_path']);canonical=declared.resolve(strict=True)
alias=Path.home()/'AppData/Local/PelloEvaluation/phase3c3-c/rubric.json'
roots=[Path(p) for p in f['deny_read_roots']]
profile='{extends=":read-only",filesystem={'+','.join(json.dumps(p.as_posix())+'="deny"' for p in roots)+'},network={enabled=false}}'
prefix=[str(Path('.venv/Lib/site-packages/codex_cli_bin/bin/codex.exe').resolve()),'-c','permissions.pello_supplied_context='+profile,'sandbox','-P','pello_supplied_context']
records=[]
for label,path in [('declared_rubric_path',declared),('normal_user_alias_path',alias)]:
    command=prefix+[sys.executable,'-B','-c','from pathlib import Path; import sys; Path(sys.argv[1]).read_bytes(); print("READ_SUCCEEDED")',str(path)]
    r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=60)
    denied=r.returncode!=0 and 'PermissionError' in r.stderr
    records.append({'path_label':label,'path':str(path),'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'denied':denied,'command':command})
    assert denied,records[-1]
proof={'declared_path':str(declared),'canonical_path':str(canonical),'normal_alias_path':str(alias),
       'parent_process_same_file':os.path.samefile(declared,canonical),'normal_alias_same_file':os.path.samefile(alias,canonical),
       'declared_sha256':hashlib.sha256(declared.read_bytes()).hexdigest(),'canonical_sha256':hashlib.sha256(canonical.read_bytes()).hexdigest(),
       'frozen_expected_sha256':f['rubric_sha256'],'native_checks':records,'rubric_or_specification_modified':False}
assert proof['parent_process_same_file'] and proof['normal_alias_same_file'] and proof['declared_sha256']==proof['canonical_sha256']==proof['frozen_expected_sha256']
(out/'rubric-c-alias-proof.json').write_text(json.dumps(proof,indent=2))
print('Exact declared key and normal-user alias reads denied; all hashes and file identity match.',flush=True)
