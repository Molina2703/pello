import copy,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
out=Path('evidence/phase3c3/contract-context-correction');out.mkdir(exist_ok=True)
core=ProductPlanningCore(Path('runtime/phase3c'));p={}
class Capture(Exception):pass
def capture(*args,**kwargs):p.update(args[4]);raise Capture()
core._invoke=capture
try:core.propose_contracts('phase3c3-heldout-f')
except Capture:pass
path=out/'original-contracts-input.json';assert not path.exists();path.write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf-8')
def size(v):return len(json.dumps(v,ensure_ascii=False,separators=(',',':')))
def table(value):
 if isinstance(value,list):
  if len(value)>1 and all(isinstance(v,dict) for v in value) and all(list(v)==list(value[0]) for v in value):
   return {'pello_table_columns':list(value[0]),'pello_table_rows':[[table(v[k]) for k in value[0]] for v in value]}
  return [table(v) for v in value]
 if isinstance(value,dict):return {k:table(v) for k,v in value.items()}
 return value
print('canonical',size(p),'table',size(table(p)))
print('requirements_fields',{k:size(v) for k,v in p['requirements'].items()})
print('increment_field_totals',{k:sum(size(i[k]) for i in p['increments']['increments']) for k in p['increments']['increments'][0]})
q=copy.deepcopy(p)
for r in q['requirements']['requirements']:r.pop('acceptance_implications',None)
print('without_provisional_requirement_criteria',size(table(q)))
for i in q['increments']['increments']:
 for k in ['components','tools','completion_conditions','verification_evidence','boundary_rationale']:i.pop(k)
print('contract_focused_full_source_and_all_authoritative_IO_interfaces_permissions_effects',size(table(q)))
