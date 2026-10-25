"""Final regression only after a valid independent held-out PASS."""
import hashlib,json,re,sqlite3,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.supervisor import files_hash

out=Path('evidence/phase3c3');evaluation=json.loads((out/'heldout-b-evaluation.json').read_text())
assert evaluation['verdict']=='PASS'
started=time.monotonic();command=[sys.executable,'-B','-m','unittest','discover','-s','tests','-v']
r=subprocess.run(command,capture_output=True,text=True,encoding='utf-8',timeout=900)
log=r.stdout+r.stderr;(out/'final-regression.log').write_text(log)
m=re.search(r'Ran (\d+) tests',log);count=int(m.group(1)) if m else 0
reg={'command':command,'exit_code':r.returncode,'tests_run':count,'tests_passed':count if r.returncode==0 else None,'seconds':round(time.monotonic()-started,3)}
(out/'final-regression.json').write_text(json.dumps(reg,indent=2));print(json.dumps(reg),flush=True)
assert r.returncode==0 and count>=227
protected=[]
for index in range(1,7):
    folder=Path('evidence/phase3c')/f'3c2-b{index}';pr=json.loads((folder/'protection.json').read_text());suite=Path('runtime/phase3c/protected')/f'3c2-b{index}'
    sources=all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in pr['hashes'].items())
    copies=files_hash(suite)==pr['suite_hash']
    checked=subprocess.run([sys.executable,'-B','-m','unittest','discover','-s',str(suite),'-p','test_*.py','-v'],capture_output=True,text=True,timeout=180)
    text=checked.stdout+checked.stderr;(out/(f'final-protected-b{index}.log')).write_text(text)
    n=int(re.search(r'Ran (\d+) tests',text).group(1))
    protected.append({'batch':index,'exit_code':checked.returncode,'tests_run':n,'source_hashes_intact':sources,'protected_copy_hash_intact':copies})
    assert checked.returncode==0 and sources and copies
(out/'final-protected.json').write_text(json.dumps(protected,indent=2))
baseline=json.loads(Path('evidence/phase3c/baseline-preservation.json').read_text())['hashes']
bad=[p for p,h in baseline.items() if not Path(p).is_file() or hashlib.sha256(Path(p).read_bytes()).hexdigest()!=h]
initial=json.loads((out/'initial-state.json').read_text());c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
old=[dict(r) for r in c.execute('select * from pello_product_operations order by rowid limit 28')]
oldmatch=hashlib.sha256(json.dumps(old,sort_keys=True).encode()).hexdigest()==initial['historical_operations_sha256']
new_protection=[]
for protection_path in [out/'isolation/protection.json',out/'isolation/profile-protection.json',out/'context-correction/protection.json']:
    value=json.loads(protection_path.read_text());new_protection += [{'file':p,'matches':hashlib.sha256(Path(p).read_bytes()).hexdigest()==h} for p,h in value['hashes'].items()]
objective_registration=json.loads((out/'objective-registration-v2.json').read_text());objective_intact=hashlib.sha256((out/'objective_checks.py').read_bytes()).hexdigest()==objective_registration['objective_script_sha256']
checkpoint_commits=[]
for row in c.execute('select project_id,phase,commit_sha from pello_product_checkpoints'):
    workspace=Path('runtime/phase3c/projects')/row['project_id']/'workspace'
    ok=subprocess.run(['git','-C',str(workspace),'cat-file','-e',row['commit_sha']+'^{commit}'],capture_output=True).returncode==0
    checkpoint_commits.append({**dict(row),'commit_present':ok})
state={'historical_hashes_checked':len(baseline),'historical_hashes_matching':len(baseline)-len(bad),'mismatches':bad,
    'first_28_sdk_operation_rows_unchanged':oldmatch,'new_protected_test_sources':new_protection,'frozen_objective_script_intact':objective_intact,
    'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],'checkpoint_commits':checkpoint_commits,
    'stop_set':Path('runtime/phase3c/STOP').exists(),'sdk_statuses':[dict(x) for x in c.execute('select status,count(*) as operations from pello_product_operations group by status')],
    'sdk_turns_consumed':c.execute('select count(*) from pello_product_operations').fetchone()[0],
    'original_projects_preserved':all(dict(c.execute('select * from pello_product_projects where project_id=?',(p['project_id'],)).fetchone())==p for p in initial['old_projects'])}
(out/'final-integrity.json').write_text(json.dumps(state,indent=2));print(json.dumps({k:v for k,v in state.items() if k!='checkpoint_commits'}),flush=True)
assert not bad and oldmatch and all(x['matches'] for x in new_protection) and objective_intact and state['sqlite_integrity']=='ok' and all(x['commit_present'] for x in checkpoint_commits) and state['original_projects_preserved']
c.close()
