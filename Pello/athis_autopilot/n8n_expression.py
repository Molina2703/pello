"""Strict parser for the small, pure expression language of the QA contract.

This recognizes syntax before any JS evaluation. There is no assignment,
destructuring, computed member, comma operator, function, or arbitrary call.
"""
import re

TOKEN=re.compile(r'''\s*(?:(\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)|('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*")|([A-Za-z_$][A-Za-z0-9_$]*)|(===|!==|&&|\|\||<=|>=|[?:.(){},+*/%!<>-]))''')
PATHS={('$json',),('Number',),('Number','isFinite')}
PATHS|={('$json',k) for k in ('body','request_id','status','result','error')}
PATHS|={('$json','body',k) for k in ('request_id','value','op')}
PATHS|={('$json','body','request_id',k) for k in ('startsWith','length')}
CALLS={('Number','isFinite'),('$json','body','request_id','startsWith')}


class PureParser:
    def __init__(self,source):
        self.tokens=[];pos=0
        while pos<len(source):
            match=TOKEN.match(source,pos)
            if not match: raise ValueError('Unrecognized pure QA expression syntax')
            self.tokens.append((match.lastindex,match.group(match.lastindex)));pos=match.end()
        if len(self.tokens)>1000: raise ValueError('QA expression token budget exceeded')
        self.tokens.append((0,'EOF'));self.index=0;self.depth=0

    def peek(self): return self.tokens[self.index][1]

    def pop(self,wanted=None):
        token=self.tokens[self.index]
        if wanted is not None and token[1]!=wanted: raise ValueError('Expected '+wanted+' in pure QA expression')
        self.index+=1
        return token

    def parse(self):
        self.conditional()
        if self.peek()!='EOF': raise ValueError('Trailing operators or statements are forbidden')

    def conditional(self):
        self.depth+=1
        if self.depth>32: raise ValueError('QA expression nesting budget exceeded')
        self.binary(0)
        if self.peek()=='?':
            self.pop('?');self.conditional();self.pop(':');self.conditional()
        self.depth-=1

    LEVELS=[{'||'},{'&&'},{'===','!=='},{'<','>','<=','>='},{'+','-'},{'*','/','%'}]

    def binary(self,level):
        if level==len(self.LEVELS): self.unary();return
        self.binary(level+1)
        while self.peek() in self.LEVELS[level]:
            self.pop();self.binary(level+1)

    def unary(self):
        if self.peek() in ('typeof','!','-','+'):
            self.pop();self.depth+=1
            if self.depth>32: raise ValueError('QA unary nesting budget exceeded')
            self.unary();self.depth-=1
        else: self.primary()

    def primary(self):
        kind,value=self.pop()
        path=None
        if value=='(':
            self.conditional();self.pop(')')
        elif value=='{':
            if self.peek()!='}':
                while True:
                    key_kind,key=self.pop()
                    if key_kind==2: key=key[1:-1]
                    if key not in {'request_id','status','result','error'}:
                        raise ValueError('Object key is outside the QA response contract')
                    self.pop(':');self.conditional()
                    if self.peek()!=',': break
                    self.pop(',')
                    if self.peek()=='}': break
            self.pop('}')
        elif kind in (1,2) or value in ('null','undefined','true','false'): pass
        elif value in ('$json','Number'): path=(value,)
        else: raise ValueError('Unauthorized primary in pure QA expression')
        while self.peek() in ('.','('):
            if self.peek()=='.':
                self.pop('.');member_kind,member=self.pop()
                if member_kind!=3 or path is None: raise ValueError('Unauthorized QA member access')
                path=(*path,member)
                if path not in PATHS: raise ValueError('Member path exceeds the QA contract')
            else:
                if path not in CALLS: raise ValueError('Arbitrary calls are forbidden')
                self.pop('(');self.conditional();self.pop(')');path=None


def validate_pure_expression(source):
    PureParser(source).parse()
