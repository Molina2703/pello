"""Bounded development evidence, using the existing protected hashes and SDK Reviewer."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from athis_autopilot.product_planning import ProductPlanningCore
from athis_autopilot.supervisor import files_hash


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['protect','verify','review','checkpoint'])
    parser.add_argument('batch')
    parser.add_argument('--tests',nargs='+',required=True)
    parser.add_argument('--files',nargs='*',default=[])
    parser.add_argument('--modules',nargs='*',default=[])
    parser.add_argument('--review-id')
    args=parser.parse_args(); batch=args.batch
    if not re.fullmatch(r'3c2-b[1-6]',batch): raise ValueError('Invalid batch')
    out=BASE/'evidence/phase3c'/batch
    out.mkdir(exist_ok=True)
    protected=BASE/'runtime/phase3c/protected'/batch
    index=out/'protection.json'
    if args.action=='protect':
        if index.exists(): raise ValueError('Frozen acceptance already registered')
        protected.mkdir(exist_ok=True,parents=True)
        hashes={}
        for test in args.tests:
            source=BASE/test;target=protected/source.name
            if not target.exists(): shutil.copyfile(source,target)
            if source.read_bytes()!=target.read_bytes(): raise ValueError('Existing frozen suite differs')
            target.chmod(0o444)
            hashes[test]=hashlib.sha256(source.read_bytes()).hexdigest()
        index.write_text(json.dumps({'hashes':hashes,'suite_hash':files_hash(protected)},indent=2)+'\n',encoding='utf-8')
        return
    frozen=json.loads(index.read_text(encoding='utf-8'))
    if files_hash(protected)!=frozen['suite_hash']: raise ValueError('Protected suite altered')
    for path,digest in frozen['hashes'].items():
        if hashlib.sha256((BASE/path).read_bytes()).hexdigest()!=digest: raise ValueError('Acceptance source altered')
    if args.action=='verify':
        command=[sys.executable,'-B','-m','unittest','discover','-s',str(protected),'-p','test_*.py','-v']
        result=subprocess.run(command,cwd=BASE,capture_output=True,text=True,encoding='utf-8',errors='replace')
        log=result.stdout+result.stderr
        (out/'protected-tests.log').write_text(log,encoding='utf-8')
        match=re.search(r'Ran (\d+) tests?',log)
        data={'command':command,'exit_code':result.returncode,'tests_run':int(match[1]) if match else 0,
              'suite_integrity':files_hash(protected)==frozen['suite_hash']}
        (out/'tests.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        print(log,flush=True)
        if result.returncode or not data['tests_run'] or not data['suite_integrity']: raise SystemExit(2)
        return
    core=ProductPlanningCore(BASE/'runtime/phase3c',timeout=240)
    try:
        pid='phase3c-c2-review'
        if args.action=='review':
            with core.db() as cx:
                exists=cx.execute('SELECT 1 FROM pello_product_projects WHERE project_id=?',(pid,)).fetchone()
            if not exists: core.create_project(BASE/'examples/phase3c/returns-desk.md',project_id=pid,max_turns=12,duration_minutes=235)
            tests=json.loads((out/'tests.json').read_text())
            if tests['exit_code'] or not tests['suite_integrity']: raise ValueError('Mandatory objective tests failed')
            diff=subprocess.run(['git','diff','HEAD','--',*args.files],cwd=BASE,capture_output=True,text=True,encoding='utf-8').stdout
            tracked=set(subprocess.run(['git','ls-files'],cwd=BASE,capture_output=True,text=True).stdout.splitlines())
            for path in [*args.files,*args.tests]:
                if path not in tracked: diff+='\nNEW FILE '+path+'\n'+(BASE/path).read_text(encoding='utf-8')
            evidence={'objective':f'{batch}: independently inspect this batch against its frozen tests and original product requirements. '+(BASE/'examples/phase3c/returns-desk.md').read_text(encoding='utf-8'),
                'changed_files':args.files,'diff':diff,'test_command':tests['command'],
                'test_exit_code':0,'tests_run':tests['tests_run'],'tests_passed':tests['tests_run'],'tests_failed':0,
                'scope_constraints':['Planning only, no product implementation or external operations.',
                    'Prior accepted batches remain in place. Only this bounded diff is being accepted.',
                    'Protected acceptance transcript:\n'+(out/'protected-tests.log').read_text(encoding='utf-8'),
                    'Actual integrated results (when available; latest revision supersedes rejected output): '+json.dumps({p.name:json.loads(p.read_text(encoding='utf-8')) for p in out.glob('live-*.json') if '-r2' in p.stem or not list(out.glob(p.stem+'-r2.json'))},ensure_ascii=False),
                    'Retained prior findings: '+json.dumps({p.name:json.loads(p.read_text(encoding='utf-8')) for p in out.glob('*-review.json')},ensure_ascii=False),
                    'No Planner reasoning is supplied. Engineering code inspected as data.']}
            (out/'review-input.json').write_text(json.dumps(evidence,indent=2)+'\n',encoding='utf-8')
            verdict=core.review_engineering_increment(pid,args.review_id or batch,evidence=evidence)
            (out/((args.review_id or batch)+'-review.json')).write_text(json.dumps(verdict,indent=2)+'\n',encoding='utf-8')
            print(json.dumps(verdict,indent=2),flush=True)
            if verdict['verdict']!='PASS': raise SystemExit(2)
        else:
            verdict=json.loads((out/((args.review_id or batch)+'-review.json')).read_text())
            if verdict['verdict']!='PASS': raise ValueError('Checkpoint requires Reviewer PASS')
            core._checkpoint('phase3c-3c1-live-r2',1,batch,evidence_dir=out,workspace_subdir=batch)
            print('ACCEPTED '+batch,flush=True)
    finally: core.backend.close()


if __name__=='__main__': main()
