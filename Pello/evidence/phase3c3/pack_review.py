"""Lossless presentation packing for an independent review, not product planning."""
import copy,re

def pack_review(packet):
    original=copy.deepcopy(packet);p=copy.deepcopy(packet);source=p['original_specification']
    for criterion in p['frozen_rubric']:
        quote=criterion.pop('source_quote')
        start=source.index(quote) if quote else None
        criterion['source_quote_ref']=None if start is None else {
            'start_character':start,'end_character':start+len(quote),
            'start_line':source[:start].count('\n')+1,'end_line':source[:start+len(quote)].count('\n')+1}
    ids=sorted(x for x in p['valid_evidence_refs'] if re.match(r'^(REQ|SRC|ISS|ASM|ASS|AC)-',x))
    aliases={value:f'E{index:03d}' for index,value in enumerate(ids,1)}
    reverse={value:key for key,value in aliases.items()}
    def walk(value,mapping):
        if isinstance(value,str):return mapping.get(value,value)
        if isinstance(value,list):return [walk(x,mapping) for x in value]
        if isinstance(value,dict):return {mapping.get(k,k):walk(v,mapping) for k,v in value.items()}
        return value
    packed=walk(p,aliases)
    packed['_reference_aliases']=reverse
    packed['_context_encoding']='E### aliases refer exactly to IDs in _reference_aliases. Frozen rubric quotation strings are represented by exact character offsets and line ranges in the complete original_specification supplied once. Expected outcomes, failure conditions and severity are unchanged. Cite supplied evidence labels or aliases.'
    restored=copy.deepcopy(packed);restored.pop('_reference_aliases');restored.pop('_context_encoding')
    restored=walk(restored,reverse)
    for criterion in restored['frozen_rubric']:
        ref=criterion.pop('source_quote_ref')
        criterion['source_quote']='' if ref is None else source[ref['start_character']:ref['end_character']]
    assert restored==original,'Reviewer context packing must reconstruct every original field exactly'
    return packed,reverse
