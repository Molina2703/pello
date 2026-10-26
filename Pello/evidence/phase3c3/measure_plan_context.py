import collections,copy,hashlib,json,re,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from athis_autopilot.product_planning import ProductPlanningCore
out=Path('evidence/phase3c3/planning-context-correction');out.mkdir(exist_ok=True)
core=ProductPlanningCore(Path('runtime/phase3c'))
class Captured(Exception):pass
def capture(*args,**kwargs):
 (out/'original-increments-input.json').write_text(json.dumps(args[4],ensure_ascii=False,indent=2),encoding='utf-8')
 raise Captured()
core._invoke=capture
try:core.propose_increments('phase3c3-heldout-e')
except Captured:pass
p=json.loads((out/'original-increments-input.json').read_text());encoded=json.dumps(p,ensure_ascii=False,separators=(',',':'))
def tables(value):
 if isinstance(value,list):
  if len(value)>1 and all(isinstance(x,dict) for x in value) and all(list(x)==list(value[0]) for x in value):
   return {'table_columns':list(value[0]),'table_rows':[[tables(x[k]) for k in value[0]] for x in value]}
  return [tables(x) for x in value]
 if isinstance(value,dict):return {k:tables(v) for k,v in value.items()}
 return value
table=tables(p);text=json.dumps(table,ensure_ascii=False,separators=(',',':'))
counts=collections.Counter()
def count(v):
 if isinstance(v,str) and re.fullmatch(r'(?:SRC|REQ|ISS|ASM)-[a-zA-Z0-9-]+',v):counts[v]+=1
 elif isinstance(v,list):
  for x in v:count(x)
 elif isinstance(v,dict):
  for x in v.values():count(x)
count(table)
mapping={v:'@'+str(i) for i,(v,n) in enumerate(counts.items()) if n>2}
def alias(v):
 if isinstance(v,str):return mapping.get(v,v)
 if isinstance(v,list):return [alias(x) for x in v]
 if isinstance(v,dict):return {k:alias(x) for k,x in v.items()}
 return v
packed=alias(table);packed['context_reference_values']={v:k for k,v in mapping.items()}
print(json.dumps({'canonical_json_characters':len(encoded),'table_json_characters':len(text),'table_and_scalar_ID_alias_characters':len(json.dumps(packed,ensure_ascii=False,separators=(',',':'))),'alias_count':len(mapping)},indent=2))
all_ids=collections.Counter(re.findall(r'(?:SRC|REQ|ISS|ASM)-[a-zA-Z0-9-]+',text))
aliases={key:'~'+str(index)+'~' for index,(key,n) in enumerate(all_ids.items()) if n>2}
assert all(a not in text for a in aliases.values())
with_aliases=re.sub(r'(?:SRC|REQ|ISS|ASM)-[a-zA-Z0-9-]+',lambda m:aliases.get(m[0],m[0]),text)
with_aliases=json.loads(with_aliases);with_aliases['context_reference_values']={v:k for k,v in aliases.items()}
print('table_and_all_ID_references',len(json.dumps(with_aliases,ensure_ascii=False,separators=(',',':'))))
all_strings=collections.Counter()
def strings(v):
 if isinstance(v,str):all_strings[v]+=1
 elif isinstance(v,list):
  for x in v:strings(x)
 elif isinstance(v,dict):
  for x in v.values():strings(x)
strings(with_aliases)
print('repeated_long_strings_potential_gain',sum((len(v)-8)*(n-1)-20 for v,n in all_strings.items() if len(v)>60 and n>1))
print('field_sizes', {k:len(json.dumps(v,ensure_ascii=False,separators=(',',':'))) for k,v in with_aliases.items()})
