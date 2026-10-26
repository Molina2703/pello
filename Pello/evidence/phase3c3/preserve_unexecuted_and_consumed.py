"""Audit preservation only, after six FAILs and user instruction to stop SDK."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3');published=[]
folder=out/'consumed-rubrics';folder.mkdir(exist_ok=True)
for letter in ['d','e','f']:
 freeze=json.loads((out/f'heldout-{letter}-freeze.json').read_text())
 assert json.loads((out/f'heldout-{letter}-evaluation.json').read_text())['verdict']=='FAIL'
 raw=Path(freeze['private_rubric_path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==freeze['rubric_sha256']
 target=folder/f'heldout-{letter}-frozen.json';assert not target.exists();target.write_bytes(raw)
 published.append({'evaluation_id':freeze['evaluation_id'],'path':str(target),'sha256':hashlib.sha256(raw).hexdigest(),'published_only_after_consumed_FAIL':True})
(out/'consumed-rubrics-def-publication.json').write_text(json.dumps({'at':datetime.now(timezone.utc).isoformat(),'rubrics':published,'frozen_expectations_modified':False},indent=2),encoding='utf-8')
files=sorted(set(out.glob('*_g.py'))|{out/'verify_rubric_g_paths.py',out/'create_g_harnesses.py'})
record={'status':'DRAFT_TOOLING_ONLY_NOT_EXECUTED','new_business_source_created':False,'new_rubric_created':False,'new_project_created':False,'SDK_calls':0,'user_decision':'Conservar el checkpoint sin ampliar','accepted_as_planning_evidence':False,'files':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}}
(out/'unexecuted-g-tooling.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({'consumed_rubrics_preserved':len(published),'unexecuted_draft_files':len(files),'new_SDK_calls':0},indent=2))
