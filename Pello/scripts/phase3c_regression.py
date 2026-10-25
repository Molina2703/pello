"""Record actual unittest exit status and totals for final acceptance."""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

base=Path(__file__).resolve().parents[1]
out=base/'evidence/phase3c/3c2-b6'
command=[sys.executable,'-B','-m','unittest','discover','-s','tests','-v']
start=time.monotonic()
result=subprocess.run(command,cwd=base,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=900)
log=result.stdout+result.stderr
(out/'final-regression.log').write_text(log,encoding='utf-8')
match=re.search(r'Ran (\d+) tests?',log)
summary={'command':command,'exit_code':result.returncode,'tests_run':int(match[1]) if match else 0,
         'elapsed_seconds':round(time.monotonic()-start,3),'passed':result.returncode==0 and bool(match)}
(out/'final-regression.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2),flush=True)
raise SystemExit(0 if summary['passed'] else 2)
