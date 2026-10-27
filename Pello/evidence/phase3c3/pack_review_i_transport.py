"""Reuse exact source references and existing row transport for review only."""
import copy,json
from pack_review import pack_review as base_pack

def pack_review(packet):
    packed,aliases=base_pack(packet)
    original=copy.deepcopy(packed)
    base_key='pello_exact_architecture_node_ref'
    assert base_key not in json.dumps(packed,ensure_ascii=False)
    factored=copy.deepcopy(packed)
    if 'functional_increments' in factored and 'architecture' in factored:
        nodes={n['task_id']:(index,n) for index,n in enumerate(factored['architecture']['nodes'])}
        for index,inc in enumerate(factored['functional_increments']['increments']):
            position,node=nodes[inc['task_id']]
            assert all(inc[k]==v for k,v in node.items())
            factored['functional_increments']['increments'][index]={base_key:position,**{k:v for k,v in inc.items() if k not in node}}
    markers={'pello_table_columns','pello_table_rows','pello_context_encoding'}
    def conflict(v):
        if isinstance(v,dict):return bool(markers.intersection(v)) or any(conflict(x) for x in v.values())
        return isinstance(v,list) and any(conflict(x) for x in v)
    assert not conflict(factored)
    def table(v):
        if isinstance(v,list):
            if len(v)>1 and all(isinstance(x,dict) for x in v) and all(list(x)==list(v[0]) for x in v):
                columns=list(v[0]);return {'pello_table_columns':columns,'pello_table_rows':[[table(x[k]) for k in columns] for x in v]}
            return [table(x) for x in v]
        if isinstance(v,dict):return {k:table(x) for k,x in v.items()}
        return v
    def untab(v):
        if isinstance(v,dict):
            if set(v)=={'pello_table_columns','pello_table_rows'}:
                return [{k:untab(x) for k,x in zip(v['pello_table_columns'],row)} for row in v['pello_table_rows']]
            return {k:untab(x) for k,x in v.items()}
        if isinstance(v,list):return [untab(x) for x in v]
        return v
    encoded=table(factored)
    encoded['pello_context_encoding']='Object lists use pello_table_columns and pello_table_rows: every row is an object with those ordered keys, recursively reconstructed unchanged. An increment with pello_exact_architecture_node_ref=N inherits ALL unchanged fields of architecture.nodes[N] (zero-based), then adds its supplied fields. Equality of every inherited field was asserted before encoding. No fact, criterion, severity, threshold, contract or scope was removed. This is transport only; use canonical evidence IDs/aliases in the verdict.'
    restored=copy.deepcopy(encoded);restored.pop('pello_context_encoding');restored=untab(restored)
    if 'functional_increments' in restored and 'architecture' in restored:
        for index,inc in enumerate(restored['functional_increments']['increments']):
            position=inc.pop(base_key)
            restored['functional_increments']['increments'][index]={**restored['architecture']['nodes'][position],**inc}
    assert restored==original
    assert json.dumps(restored,ensure_ascii=False,sort_keys=True)==json.dumps(original,ensure_ascii=False,sort_keys=True)
    return encoded,aliases
