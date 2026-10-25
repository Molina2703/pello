"""Bounded credential-free QA contract and three-node source verifier."""
import json
import os
import re
import shutil
import subprocess
from typing import Literal

from .messages import Message, Text
from .n8n_operations import digest
from .n8n_expression import validate_pure_expression


class QAContract(Message):
    workflow_name: Text
    webhook_path: Text
    request_id_prefix: Literal['pello-3b-']
    operation: Literal['double']
    value_min: Literal[-1000000]
    value_max: Literal[1000000]
    success_http_status: Literal[200]
    invalid_http_status: Literal[400]


NODE_TYPES = [('QA Webhook','n8n-nodes-base.webhook',2.2),
              ('QA Result','n8n-nodes-base.set',3.5),
              ('QA Response','n8n-nodes-base.respondToWebhook',1.5)]


def expression(value):
    if not isinstance(value,str) or not value.strip().startswith('={{') or not value.strip().endswith('}}'):
        raise ValueError('Expected a bounded n8n expression')
    text=value.strip()[3:-2].strip()
    if len(text)>3000 or any(token in text for token in ('[',']','`',';','=>','/*','//')):
        raise ValueError('Expression syntax exceeds pure QA scope')
    validate_pure_expression(text)
    return text


def validate_blueprint(value, contract):
    if not isinstance(value,dict) or set(value)!={'nodes'} or not isinstance(value['nodes'],list) or len(value['nodes'])!=3:
        raise ValueError('Only the three-node QA blueprint is authorized')
    for node,(name,kind,version) in zip(value['nodes'],NODE_TYPES):
        if set(node)!={'name','type','version','parameters'} or (node['name'],node['type'],node['version'])!=(name,kind,version):
            raise ValueError('Unauthorized node type, version, identity or credential field')
        if not isinstance(node['parameters'],dict): raise ValueError('Node parameters must be an object')
    webhook,transform,response=[n['parameters'] for n in value['nodes']]
    if (not set(webhook)<= {'httpMethod','path','responseMode','authentication','options'} or
        webhook.get('httpMethod')!='POST' or webhook.get('path')!=contract.webhook_path or
        webhook.get('responseMode')!='responseNode' or webhook.get('authentication','none')!='none' or webhook.get('options',{})):
        raise ValueError('Webhook must use the project QA route and response node, without credentials')
    if (not set(transform)<= {'mode','jsonOutput','options','includeOtherFields'} or transform.get('mode')!='raw' or
            transform.get('options',{}) or transform.get('includeOtherFields',False)):
        raise ValueError('Only isolated JSON output is permitted')
    expression(transform.get('jsonOutput'))
    if not set(response)<= {'respondWith','responseBody','options'} or response.get('respondWith')!='json':
        raise ValueError('Only JSON webhook responses are permitted')
    expression(response.get('responseBody'))
    if set(response.get('options',{}))!={'responseCode'}: raise ValueError('Only explicit response status is permitted')
    expression(response['options']['responseCode'])
    return value


def cases(contract):
    def body(label,value=21,op='double',request_id=None):
        return {'request_id':request_id or contract.request_id_prefix+label,'value':value,'op':op}
    inputs=[body('valid'),body('invalid','not-a-number'),body('negative',-3),body('zero',0),
            body('boolean',True),body('operation',2,'other'),body('bounds',1000001),
            {'value':4,'op':'double'},body('prefix',2,request_id='not-qa')]
    result=[]
    for payload in inputs:
        value=payload.get('value'); identifier=payload.get('request_id')
        valid=(isinstance(identifier,str) and identifier.startswith(contract.request_id_prefix) and payload.get('op')==contract.operation
            and isinstance(value,(int,float)) and not isinstance(value,bool) and contract.value_min<=value<=contract.value_max)
        expected=({'request_id':identifier,'status':'ok','result':value*2} if valid else
                  {'request_id':identifier if isinstance(identifier,str) else None,'status':'invalid','error':'invalid_input'})
        result.append({'payload':payload,'http_status':200 if valid else 400,'expected':expected})
    return result


def check_cases(blueprint,contract):
    validate_blueprint(blueprint,contract)
    node=shutil.which('node')
    if not node: raise ValueError('Installed Node.js is required for isolated expression verification')
    payload={'transform':expression(blueprint['nodes'][1]['parameters']['jsonOutput']),
             'response':expression(blueprint['nodes'][2]['parameters']['responseBody']),
             'status':expression(blueprint['nodes'][2]['parameters']['options']['responseCode']), 'cases':cases(contract)}
    driver="""const vm=require('node:vm');let input='';process.stdin.on('data',c=>input+=c);process.stdin.on('end',()=>{
const d=JSON.parse(input);const evaluate=(code,json)=>{const c=vm.createContext({},{codeGeneration:{strings:false,wasm:false}});vm.runInContext('var $json=JSON.parse('+JSON.stringify(JSON.stringify(json))+')',c,{timeout:100});return vm.runInContext('('+code+')',c,{timeout:100});};
const out=d.cases.map(c=>{let item=evaluate(d.transform,{body:c.payload});if(typeof item==='string')item=JSON.parse(item);return {body:evaluate(d.response,item),status:evaluate(d.status,item)};});process.stdout.write(JSON.stringify(out));});"""
    env={k:v for k,v in os.environ.items() if k.upper() in {'PATH','SYSTEMROOT','WINDIR','COMSPEC','TEMP','TMP'}}
    run=subprocess.run([node,'-e',driver],input=json.dumps(payload),capture_output=True,text=True,encoding='utf-8',env=env,timeout=10)
    if run.returncode: raise ValueError('QA expression evaluation failed: '+run.stderr[-1200:])
    observed=json.loads(run.stdout)
    return [{**case,'observed':actual,'passed':actual['body']==case['expected'] and actual['status']==case['http_status']}
            for case,actual in zip(payload['cases'],observed)]


def sdk_code(blueprint,contract):
    validate_blueprint(blueprint,contract)
    def render(value):
        if isinstance(value,str) and value.strip().startswith('={{'):
            expression(value)
            return 'expr('+json.dumps(value.strip()[1:])+')'
        if isinstance(value,dict): return '{'+','.join(json.dumps(k)+':'+render(v) for k,v in value.items())+'}'
        if isinstance(value,list): return '['+','.join(render(v) for v in value)+']'
        return json.dumps(value,ensure_ascii=False)
    lines=["import { workflow, trigger, node, expr } from '@n8n/workflow-sdk';"]
    for index,source in enumerate(blueprint['nodes']):
        item={'type':source['type'],'version':source['version'],'config':{'name':source['name'],'parameters':source['parameters']}}
        lines.append('const n'+str(index)+' = '+('trigger' if index==0 else 'node')+'('+render(item)+');')
    lines.append('export default workflow('+json.dumps(contract.webhook_path)+','+json.dumps(contract.workflow_name)+').add(n0).to(n1).to(n2);')
    return '\n'.join(lines)


def verify_remote(remote,blueprint,contract):
    validate_blueprint(blueprint,contract)
    if remote.get('name')!=contract.workflow_name or not remote.get('id') or not remote.get('versionId'):
        raise ValueError('Remote resource identity/version is unconfirmed')
    if remote.get('pinData') or remote.get('settings',{}).get('errorWorkflow'):
        raise ValueError('Pinned data and other workflow effects are not permitted')
    nodes=remote.get('nodes',[])
    if len(nodes)!=3 or {n['name'] for n in nodes}!={n[0] for n in NODE_TYPES}:
        raise ValueError('Remote graph contains unexpected nodes')
    for expected in blueprint['nodes']:
        actual=next(n for n in nodes if n['name']==expected['name'])
        if actual.get('credentials') or actual.get('disabled') or actual['type']!=expected['type'] or actual['typeVersion']!=expected['version']:
            raise ValueError('Remote node credentials/type/version do not match safe source')
        parameters=actual.get('parameters',{})
        if not set(parameters)<=set(expected['parameters'])|{'options','includeOtherFields'}:
            raise ValueError('Remote node has unreviewed parameters')
        for key in set(parameters)-set(expected['parameters']):
            if (key=='options' and parameters[key]!={}) or (key=='includeOtherFields' and parameters[key] is not False):
                raise ValueError('Remote node has an unreviewed nondefault parameter')
        for key,value in expected['parameters'].items():
            if parameters.get(key)!=value: raise ValueError('Remote parameter differs from source: '+expected['name']+'/'+key)
    edges=[]
    for source,types in remote.get('connections',{}).items():
        for kind,outputs in types.items():
            for output,targets in enumerate(outputs):
                edges.extend((source,t['node'],kind,output,t['index']) for t in targets)
    if sorted(edges)!=sorted([('QA Webhook','QA Result','main',0,0),('QA Result','QA Response','main',0,0)]):
        raise ValueError('Remote connections do not match the isolated linear workflow')
    return True


def fingerprint(remote):
    return digest({'nodes':sorted([{k:n.get(k) for k in ('name','type','typeVersion','parameters','credentials','disabled')}
                                  for n in remote['nodes']],key=lambda n:n['name']),
                   'connections':remote['connections'],'settings':remote.get('settings',{})})
