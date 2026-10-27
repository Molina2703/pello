"""Read-only accounting/reconstruction with a new named SQLite backup."""
import hashlib,json,re,sqlite3,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
label=sys.argv[1];assert re.fullmatch(r'checkpoint-\d+',label)
out=Path('evidence/phase3c3');dest=out/(label+'-jobs.sqlite3');state_file=out/(label+'-state.json')
assert not dest.exists() and not state_file.exists()
c=sqlite3.connect(Path('runtime/phase3c/jobs.sqlite3').resolve().as_uri()+'?mode=ro',uri=True);c.row_factory=sqlite3.Row
ops=[dict(x) for x in c.execute('select * from pello_product_operations order by rowid')]
statuses={}
for op in ops:statuses[op['status']]=statuses.get(op['status'],0)+1
assert set(statuses)<={'COMPLETED','NOT_SUBMITTED_CONTEXT_REJECTED','FAILED_PROVIDER_QUOTA_RECONCILED','NOT_SUBMITTED_ACTIVE_WRITER_RECONCILED'}
auth=[dict(x) for x in c.execute('select * from pello_product_run_authorizations order by rowid')]
projects=[dict(x) for x in c.execute('select * from pello_product_projects order by rowid')]
assert len(ops)==sum(x['used_turns'] for x in projects)<=auth[-1]['max_turns']==114
assert datetime.now(timezone.utc)<datetime.fromisoformat(auth[-1]['deadline'])
old=sqlite3.connect(Path('evidence/phase3c3/checkpoint-88-jobs.sqlite3').resolve().as_uri()+'?mode=ro',uri=True);old.row_factory=sqlite3.Row
assert [dict(x) for x in old.execute('select * from pello_product_operations order by rowid')]==ops[:88];old.close()
checkpoints=[dict(x) for x in c.execute('select * from pello_product_checkpoints order by rowid')]
for cp in checkpoints:
    w=Path('runtime/phase3c/projects')/cp['project_id']/'workspace'
    assert subprocess.run(['git','-C',str(w),'cat-file','-e',cp['commit_sha']+'^{commit}'],capture_output=True).returncode==0
core=ProductPlanningCore(Path('runtime/phase3c'))
c2=core.reconstruct_plan('phase3c-3c1-live-r2');case=core.reconstruct_plan('phase3c3-heldout-i');inspection=core.inspect_plan('phase3c3-heldout-i')
assert c.execute('select count(*) from pello_product_operations').fetchone()[0]==len(ops)
assert case['approval']=='PROPOSED' and c2['approval']=='ACCEPTED'
assert c2['plan_sha256']=='7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87'
assert case['plan_sha256']=='b0199c77c21c1e0b66ffd2f2b6217a011c95760bb87f0cc4957b930233c5a722'
assert not inspection['execution_authorized'] and not Path('runtime/phase3c/STOP').exists()
freeze=json.loads((out/'heldout-i-freeze.json').read_text())
assert hashlib.sha256((out/'heldout-i-spec.md').read_bytes()).hexdigest()==freeze['specification_sha256']
assert hashlib.sha256(Path(freeze['private_rubric_path']).read_bytes()).hexdigest()==freeze['rubric_sha256']
failures={x:json.loads((out/f'heldout-{x}-evaluation.json').read_text())['verdict'] for x in 'abcdefghi'};assert set(failures.values())=={'FAIL'}
backup=sqlite3.connect(dest);c.backup(backup);backup.close()
state={'at':datetime.now(timezone.utc).isoformat(),'HEAD':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],text=True).strip(),
 'phase3c3':'PARTIAL','overall_phase3c':'PARTIAL','blind_generalization':'UNVERIFIED','execution':'BOUNDED_CASE_FINISHED_NO_FRESH_CASE_CAPACITY',
 'cumulative_limit':114,'charged_reservations':len(ops),'completed_SDK_calls':statuses['COMPLETED'],'statuses':statuses,'remaining_global_slots':114-len(ops),
 'author_used_max':[[p['used_turns'],p['max_turns']] for p in projects if p['project_id']=='phase3c3-author'][0],
 'deadline':auth[-1]['deadline'],'STOP':False,'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],
 'first_88_operation_rows_unchanged':True,'checkpoints':checkpoints,'all_checkpoint_Git_objects_present':True,
 'C2_accepted_plan_digest':c2['plan_sha256'],'I_proposed_plan_digest':case['plan_sha256'],'I_plan_approval':case['approval'],'I_first_actionable':inspection['first_actionable'],
 'nine_original_FAILs':failures,'I_semantic_score':{'critical_passed':23,'critical_total':24,'passed':24,'total':25,'fraction':0.96,'verdict':'FAIL'},
 'snapshot_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'backup_path':str(dest),'external_business_operations':0,'business_Coder_calls':0,'Phase3D_started':False,
 'accepted_engineering_checkpoint':json.loads((out/'engineering-checkpoint-i.json').read_text()),'full_regression':json.loads((out/'model-capacity-regression.json').read_text()),
 'protected_C2':63,'protected_C3':44,'protected_C3_sources':12,'historical_hashes':1493,'no_case_J_started':True,'no_case_I_rerun_after_implementation_change':True}
state_file.write_text(json.dumps(state,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in state.items() if k not in ['checkpoints','full_regression','accepted_engineering_checkpoint','statuses']},indent=2));c.close()
