"""Small n8n QA extension of the existing incremental pipeline, not a new engine."""
import json
from pathlib import Path
import shutil
import time
from uuid import uuid4

from pydantic import TypeAdapter
from .ai_supervisor import ROLE_INSTRUCTIONS, SDKBackend
from .engines import CodexBlocked
from .messages import Identifier, parse_response
from .model_policy import probe_capabilities, select_model
from .n8n_operations import N8nJournal, mcp_data, digest
from .n8n_qa import QAContract, validate_blueprint, check_cases, sdk_code, verify_remote, fingerprint, cases
from .pipeline import IncrementalPipeline, write_json, encoded
from .pipeline_contracts import PipelinePolicy
from .supervised import workspace_snapshot
from .supervisor import now


DRAFT_TESTS = '''import json
from pathlib import Path
import unittest
from athis_autopilot.n8n_qa import QAContract, validate_blueprint, check_cases, verify_remote
class DraftAcceptance(unittest.TestCase):
    def setUp(self):
        self.contract=QAContract.model_validate_json(Path(__file__).with_name('contract.json').read_text())
        self.source=json.loads(Path('workflow.json').read_text())
    def test_safe_source_structure(self): validate_blueprint(self.source,self.contract)
    def test_independent_contract_cases(self): self.assertTrue(all(c['passed'] for c in check_cases(self.source,self.contract)))
    def test_remote_definition_matches_source(self):
        evidence=json.loads(Path('remote-draft.json').read_text()); verify_remote(evidence['workflow'],self.source,self.contract)
    def test_actual_identity_version_and_mcp_exposure(self):
        e=json.loads(Path('remote-draft.json').read_text())
        self.assertTrue(e['workflow']['id']); self.assertTrue(e['workflow']['versionId'])
        self.assertEqual(e['workflow']['id'],e['workflow_id'])
        self.assertFalse(e['workflow']['active']); self.assertTrue(e['mcp_available']); self.assertTrue(e['official_validation']['valid'])
    def test_real_manual_execution_results(self):
        e=json.loads(Path('remote-draft.json').read_text()); self.assertEqual(len(e['manual_cases']),2)
        for case in e['manual_cases']:
            self.assertTrue(case['execution_id']); self.assertEqual(case['observed_output'],case['expected']); self.assertTrue(case['passed'])
'''
PUBLISHED_TESTS = '''import json
from pathlib import Path
import unittest
from athis_autopilot.n8n_qa import QAContract, verify_remote
class PublishedAcceptance(unittest.TestCase):
    def test_published_qa_evidence(self):
        e=json.loads(Path('remote-published.json').read_text())
        c=QAContract.model_validate_json(Path(__file__).with_name('contract.json').read_text())
        verify_remote(e['workflow'],json.loads(Path('workflow.json').read_text()),c)
        self.assertTrue(e['workflow']['active']); self.assertTrue(e['verified'])
        self.assertEqual(e['workflow']['activeVersionId'],e['reviewed_version'])
        self.assertEqual(e['workflow']['id'],e['workflow_id'])
        self.assertEqual([x['name'] for x in e['http_cases']],['valid','invalid-type','negative','repeat-valid'])
        for case in e['http_cases']:
            self.assertEqual(case['status'],case['expected_status'])
            self.assertEqual(case['body'],case['expected_body'])
            self.assertTrue(case['passed'])
        self.assertTrue(e['execution_results'])
        for execution in e['execution_results']:
            self.assertTrue(execution['id']); self.assertTrue(execution['successful'])
            self.assertEqual(execution['workflow_id'],e['workflow_id'])
'''


def final_execution_output(data,workflow_id,execution_id):
    execution=data.get('execution') or {}
    if str(execution.get('id'))!=str(execution_id) or execution.get('workflowId')!=workflow_id:
        raise CodexBlocked('Execution identity differs from the requested owned resource')
    status=execution.get('status')
    if status in ('error','canceled','crashed','unknown'):
        raise CodexBlocked('QA execution ended without success: '+status)
    if status!='success': return None
    result=(data.get('data') or {}).get('resultData') or {}
    if result.get('error'): raise CodexBlocked('QA execution contains a result error')
    if result.get('lastNodeExecuted')!='QA Response': return None
    runs=(result.get('runData') or {}).get('QA Response') or []
    if len(runs)!=1 or runs[0].get('error'): return None
    outputs=(runs[0].get('data') or {}).get('main') or []
    if len(outputs)!=1 or len(outputs[0])!=1: return None
    return outputs[0][0].get('json')


class N8nPipeline(IncrementalPipeline):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.journal=N8nJournal(self)

    def create_qa_project(self, *, project_id=None):
        with self.db() as cx:
            if cx.execute('SELECT 1 FROM pello_n8n_projects').fetchone():
                raise CodexBlocked('This pilot already has a project; resume it instead of creating another workflow')
        project_id=project_id or 'phase3b-qa-'+uuid4().hex[:12]
        TypeAdapter(Identifier).validate_python(project_id)
        token=uuid4().hex[:20]
        scope={'workflow_name':'PELLO-3B-MCP-INTEGRATION-QA-'+token,
            'webhook_path':'pello-3b-'+token,'request_id_prefix':'pello-3b-', 'operation':'double',
            'value_min':-1000000,'value_max':1000000,'success_http_status':200,'invalid_http_status':400}
        folder=self.root/'contracts'/project_id; workspace=folder/'workspace'
        workspace.mkdir(parents=True,exist_ok=False); self.git(workspace,'Pello QA contract context')
        policy=PipelinePolicy(max_turns=10,max_attempts=2)
        capabilities=self.backend.capabilities() if hasattr(self.backend,'capabilities') else probe_capabilities()
        selection=select_model(policy,capabilities,phase='plan')
        prompt=('Define the exact technical contract for this synthetic QA pilot before Tester prepares tests. '
            'No tools or file changes. Return the requested contract JSON using the authorized scope unchanged. '
            'Input JSON: request_id string starting with request_id_prefix, value finite number (not boolean) in bounds, '
            'op=double. Valid response {request_id,status:ok,result:value*2}, HTTP 200. Invalid response '
            '{request_id:the supplied string or null,status:invalid,error:invalid_input}, HTTP 400. '
            'Three nodes only: webhook -> edit fields -> JSON response. No credentials or external effects.\n'
            'QA CONTRACT SCOPE (JSON):\n'+encoded(scope))
        raw=self.backend.run(workspace=workspace,thread_file=folder/'planner-thread.txt',out_dir=folder/'planner',
            role='planner',model=selection['model'],effort=selection['effort'],prompt=prompt,
            schema=QAContract.model_json_schema(),timeout=self.timeout,session_db=None,project_id=None,task_id=None)
        contract=parse_response(QAContract,raw['final_response'])
        if contract.model_dump()!=scope: raise CodexBlocked('Planner contract changed the authorized QA scope')
        # Deterministic Tester prepares and protects suites only after Planner's contract exists.
        suite=folder/'acceptance'
        for name,tests in (('draft',DRAFT_TESTS),('published',PUBLISHED_TESTS)):
            target=suite/name; target.mkdir(parents=True)
            write_json(target/'contract.json',contract.model_dump())
            (target/('test_'+name+'.py')).write_text(tests,encoding='utf-8')
        spec=folder/'SPEC.md'
        spec.write_text('Synthetic n8n MCP QA only. Do not access HMP workflows, credentials or customer services.\n'
            'Contract: '+encoded(scope)+'\nValid: {request_id,status:"ok",result:value*2}; invalid: '
            '{request_id:string or null,status:"invalid",error:"invalid_input"}.\n'
            'Webhook -> Edit Fields -> Respond to Webhook only. No Code, HTTP Request, schedule, credentials or other workflows.\n',encoding='utf-8')
        manifest={'architecture_constraints':['One new credential-free QA workflow only; no HMP changes',
            'Coder writes JSON artifacts only; Core performs authorized native MCP calls'], 'tools':[], 'increments':[]}
        for task,components,suite_name,count,deps,instruction in (
            ('DRAFT',['workflow.json','remote-draft.json'],'draft',5,[],
             'Write only workflow.json: object {nodes:[...]}. Each node has exactly name,type,version,parameters. '
             'Ordered nodes QA Webhook/n8n-nodes-base.webhook/2.2; QA Result/n8n-nodes-base.set/3.5; '
             'QA Response/n8n-nodes-base.respondToWebhook/1.5. Set uses mode raw and jsonOutput expression; '
             'respondWith json, responseBody expression, options.responseCode expression. All expressions must be pure '
             'n8n ={{ ... }} with $json, body fields, Number.isFinite, typeof, startsWith, ternaries and literal bounds. '
             'No arrays/computed property access, functions, loops, globals, credentials or network. '
             'Implement the contract exactly; no extra response fields. Core writes remote-draft.json; do not manufacture it.'),
            ('PUBLISH',['publication.json','remote-published.json'],'published',1,['DRAFT'],
             'Write only publication.json: {action:"publish",workflow_id:<recorded own ID>,version_id:<reviewed version>}. '
             'Do not change workflow.json or perform external operations. Core publishes and independently verifies the reviewed version.')):
            manifest['increments'].append({'task_id':task,'specification':instruction,'inputs':['Approved QA contract and objective evidence'],
                'outputs':components,'components':components,'acceptance_criteria':['Contract and mandatory independent verification pass'],
                'depends_on':deps,'suite':suite_name,'expected_tests':count,'risk':'routine'})
        manifest_path=folder/'increments.json'; write_json(manifest_path,manifest)
        pid=self.create_pipeline(spec,suite,manifest_path,policy=policy,project_id=project_id)
        self.journal.configure(pid,scope['workflow_name'],scope['webhook_path'],seconds=3600)
        shutil.copy2(folder/'planner-thread.txt',self.folder(pid)/'planner-thread.txt')
        with self.db() as cx:
            cx.execute('INSERT INTO pello_sessions VALUES(?,?,?,?,?,?,?)',
                (pid,'planner',raw['thread_id'],now(),raw['turn_id'],None,'READY'))
        self.current_selection=selection
        self.reserve(pid,'contract',{'role':'planner','thread_id':raw['thread_id'],'prompt':prompt,'schema':QAContract.model_json_schema()})
        self.save_response(pid,'contract',raw)
        return pid

    def contract(self,pid):
        contract=QAContract.model_validate_json((self.folder(pid)/'acceptance/draft/contract.json').read_text(encoding='utf-8'))
        resource=self.journal.resource(pid)
        if (contract.workflow_name,contract.webhook_path)!=(resource['name'],resource['webhook_path']):
            raise CodexBlocked('Protected contract differs from recorded resource scope')
        return contract

    def _context(self,project,task=None,attempt=None):
        context=super()._context(project,task,attempt)
        context.update(n8n_qa_contract=self.contract(project['id']).model_dump(),n8n_resource=self.journal.resource(project['id']),
            tool_policy='Coder edits scoped JSON only. Core uses the official SDK MCP transport with journal/limits. No manual external actions.')
        return context

    def _manual_case(self,pid,key,case):
        resource=self.journal.resource(pid)
        response=self.journal.call(pid,key,'execute_workflow',{'workflowId':resource['workflow_id'],'executionMode':'manual',
            'triggerNodeName':'QA Webhook','inputs':{'webhookData':{'method':'POST','body':case['payload']}}})
        data=mcp_data(response)
        execution_id=data.get('executionId') or (data.get('execution') or {}).get('id')
        if execution_id is None: raise CodexBlocked('MCP execution response has no confirmed execution ID')
        observed=None
        for poll in range(3):
            if observed is not None: break
            if poll: time.sleep(2)
            read=self.journal.call(pid,key+'-result-'+str(poll),'get_workflow_execution',
                {'workflowId':resource['workflow_id'],'executionId':str(execution_id),'includeData':True,'truncateData':2})
            observed=final_execution_output(mcp_data(read),resource['workflow_id'],execution_id)
        if observed is None: raise CodexBlocked('QA execution output is not yet verified; do not repeat execution blindly')
        return {**case,'execution_id':str(execution_id),'observed_output':observed,'passed':observed==case['expected']}

    def _execute_increment(self,project,task,attempt):
        if task['task_id']=='PUBLISH': raise CodexBlocked('Publication implementation belongs to the next checkpoint, 3B3')
        super()._execute_increment(project,task,attempt)
        pid=project['id']; workspace=self.folder(pid)/'workspace'; contract=self.contract(pid)
        try:
            blueprint=json.loads((workspace/'workflow.json').read_text(encoding='utf-8'))
            validate_blueprint(blueprint,contract)
            local=check_cases(blueprint,contract)
            if not all(c['passed'] for c in local): raise ValueError('Deterministic contract cases failed: '+encoded(local))
        except (ValueError,KeyError,TypeError) as exc:
            self._advance_attempt(pid,task['task_id'],attempt['attempt'],'FAILED',feedback='Local pre-MCP acceptance failure: '+str(exc))
            return
        code=sdk_code(blueprint,contract); prefix='draft-'+str(attempt['attempt'])
        validation=mcp_data(self.journal.call(pid,prefix+'-validate','validate_workflow',{'code':code}))
        if validation.get('valid') is not True:
            self._advance_attempt(pid,task['task_id'],attempt['attempt'],'FAILED',feedback='Official workflow validation failed: '+encoded(validation))
            return
        resource=self.journal.resource(pid)
        if not resource['workflow_id']:
            existing=mcp_data(self.journal.call(pid,'search-before-create','search_workflows',{'query':resource['name'],'limit':20}))
            if existing.get('data'): raise CodexBlocked('QA name already exists; reconcile instead of creating')
            self.journal.call(pid,'create','create_workflow_from_code',{'code':code,'name':resource['name'],
                'description':'Pello Phase 3B synthetic credential-free integration QA','versionName':'Initial QA contract'})
        else:
            self.journal.call(pid,prefix+'-update','update_workflow',{'workflowId':resource['workflow_id'],
                'operations':[{'type':'updateNodeParameters','nodeName':n['name'],'parameters':n['parameters'],'replace':True} for n in blueprint['nodes']],
                'versionName':'Localized QA correction'})
        resource=self.journal.resource(pid)
        detail=mcp_data(self.journal.call(pid,prefix+'-details','get_workflow_details',{'workflowId':resource['workflow_id']}))
        remote=detail['workflow']; verify_remote(remote,blueprint,contract)
        if remote['id']!=resource['workflow_id']: raise CodexBlocked('Remote readback ID differs from the journaled workflow ID')
        if remote.get('active'): raise CodexBlocked('New draft unexpectedly published before review')
        listing=mcp_data(self.journal.call(pid,prefix+'-exposure','search_workflows',{'query':resource['name'],'limit':20}))
        available=any(item.get('id')==resource['workflow_id'] and item.get('availableInMCP') is True for item in listing.get('data',[]))
        if not available: raise CodexBlocked('New workflow MCP exposure is not confirmed')
        manual=[self._manual_case(pid,prefix+'-case-'+str(i),case) for i,case in enumerate(cases(contract)[:2])]
        write_json(workspace/'remote-draft.json',{'workflow':remote,'workflow_id':resource['workflow_id'],'official_validation':validation,
            'mcp_available':available,'manual_cases':manual,'blueprint_sha256':digest(blueprint)})
        self._advance_attempt(pid,task['task_id'],attempt['attempt'],'EXECUTED',after_snapshot=encoded(workspace_snapshot(workspace)))

    def _finish_review(self,project,task,attempt):
        super()._finish_review(project,task,attempt)
        if task['task_id']=='DRAFT' and self.attempts(project['id'],task['task_id'])[-1]['stage']=='REVIEWED':
            evidence=json.loads((self.folder(project['id'])/'workspace/remote-draft.json').read_text())
            self.journal.reviewed(project['id'],evidence['workflow']['versionId'],fingerprint(evidence['workflow']),
                                  tests_passed=True,review_passed=True)

    def pipeline_report(self,pid):
        report=super().pipeline_report(pid); resource=self.journal.resource(pid)
        report.update(workflow_id=resource['workflow_id'],external_operations=self.journal.operations(pid),
            external_integration=('TESTED WITH MOCKS' if type(self.backend) is not SDKBackend else
                'DRAFT REAL MCP VERIFIED; PUBLISHING PENDING' if report['verified_increments'] else 'PENDING'))
        write_json(self.folder(pid)/'pipeline-report.json',report)
        (self.folder(pid)/'pipeline-report.md').write_text('# Pello n8n QA\n\nEstado: '+report['stage']+
            '\nIntegración: '+report['external_integration']+'\nWorkflow ID: '+str(resource['workflow_id'])+
            '\nV1 completo: pendiente\n',encoding='utf-8')
        return report

    def run_pipeline(self,pid,*,stop_after=None):
        if (self.folder(pid)/'STOP').exists():
            with self.db() as cx: self.set_stage(cx,pid,'PAUSED',blocker='Emergency STOP set')
            return self.pipeline_report(pid)
        return super().run_pipeline(pid,stop_after=stop_after)
