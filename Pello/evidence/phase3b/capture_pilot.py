"""Snapshot the isolated Phase 3B runtime without global config/auth or Git objects."""
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

phase,pid=sys.argv[1:]
project=Path(__file__).resolve().parents[2]
runtime=project/'runtime/phase3b'
out=project/'evidence/phase3b'/phase
out.mkdir(exist_ok=False)
for source,name in ((runtime/'supervised'/pid,'project'),(runtime/'contracts'/pid,'contract-stage')):
    shutil.copytree(source,out/name,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.lock'))
with sqlite3.connect(runtime/'jobs.sqlite3') as cx:
    cx.row_factory=sqlite3.Row
    tables=[r[0] for r in cx.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    dump={table:[dict(r) for r in cx.execute('SELECT * FROM "'+table+'"')] for table in tables}
(out/'sqlite-state.json').write_text(json.dumps(dump,ensure_ascii=False,indent=2),encoding='utf-8')
workspace=runtime/'supervised'/pid/'workspace'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=workspace,text=True).strip()
(out/'workspace-head.txt').write_text(head+'\n',encoding='utf-8')
hashes={p.relative_to(out).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.rglob('*')) if p.is_file()}
(out/'sha256.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(json.dumps({'snapshot':str(out),'files':len(hashes),'workspace_head':head}))
