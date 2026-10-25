"""Fake models/MCP with real pipeline, Node expression tests, SQLite and Git."""
import json
from pathlib import Path
import tempfile
import unittest
from uuid import uuid4

from pipeline_support import PipelineBackend
from test_n8n_qa import blueprint_fixture
from test_n8n_operations import result
from athis_autopilot.n8n_pipeline import N8nPipeline
from athis_autopilot.n8n_operations import mcp_data
from athis_autopilot.engines import CodexBlocked


class PilotBackend(PipelineBackend):
    def __init__(self):
        super().__init__(); self.remote=[]; self.workflow=None; self.credentials=False; self.executions={}
    def run(self, **kwargs):
        thread=kwargs['thread_file']
        if not thread.exists(): self.prepare(workspace=kwargs['workspace'],thread_file=thread,out_dir=kwargs['out_dir'],
                                              role=kwargs['role'],model=kwargs['model'],effort=kwargs['effort'])
        if 'QA CONTRACT SCOPE (JSON):\n' in kwargs['prompt']:
            payload=json.loads(kwargs['prompt'].split('QA CONTRACT SCOPE (JSON):\n')[1])
        else:
            data=json.loads(kwargs['prompt'].split('PIPELINE CONTEXT (JSON):\n')[1]); phase=kwargs['out_dir'].name
            if phase=='plan':
                payload={'project_id':data['project_id'],'architecture':['Three credential-free nodes'],
                    'tasks':[{'task_id':t['task_id'],'objective':t['specification'],'implementation_instruction':t['specification']}
                             for t in data['owner_contract']['increments']],'reasoning_summary':'Injected planning'}
            elif phase=='execute':
                assert (kwargs['workspace'].parent/'acceptance/draft/contract.json').exists()
                blueprint=blueprint_fixture(); blueprint['nodes'][0]['parameters']['path']=data['n8n_qa_contract']['webhook_path']
                self.blueprint=blueprint
                (kwargs['workspace']/'workflow.json').write_text(json.dumps(blueprint))
                payload={'project_id':data['project_id'],'task_id':'DRAFT','execution_summary':'Injected blueprint',
                         'files_modified':['workflow.json'],'errors':[],'evidence_paths':[]}
            else:
                payload={'project_id':data['project_id'],'task_id':data['current_increment']['owner']['task_id'],
                         'attempt':data['attempt']['attempt'],'verdict':'PASS','diagnosis':'none','feedback':'Injected review'}
        raw={'status':'completed','thread_id':thread.read_text(),'turn_id':'injected-'+uuid4().hex,
             'final_response':json.dumps(payload),'usage':None}
        kwargs['out_dir'].mkdir(parents=True,exist_ok=True)
        (kwargs['out_dir']/'codex_result.json').write_text(json.dumps(raw))
        return raw
    def mcp(self, **kwargs):
        req=kwargs['request']; self.remote.append(req); args=req['arguments']; tool=req['tool']
        if tool=='validate_workflow': return result({'valid':True,'nodeCount':3})
        if tool=='create_workflow_from_code':
            self.workflow={'id':'mock-owned-workflow','name':args['name'],'versionId':'mock-v1','active':False,
                'nodes':[{'name':n['name'],'type':n['type'],'typeVersion':n['version'],'parameters':n['parameters']}
                         for n in self.blueprint['nodes']],
                'connections':{'QA Webhook':{'main':[[{'node':'QA Result','type':'main','index':0}]]},
                               'QA Result':{'main':[[{'node':'QA Response','type':'main','index':0}]]}},'settings':{}}
            if self.credentials:self.workflow['nodes'][0]['credentials']={'customer':{'id':'forbidden-reference'}}
            return result({'workflowId':self.workflow['id']})
        if tool=='search_workflows': return result({'data':[] if not self.workflow else
            [{'id':self.workflow['id'],'name':self.workflow['name'],'availableInMCP':True}]})
        if tool=='get_workflow_details': return result({'workflow':self.workflow})
        if tool=='execute_workflow':
            body=args['inputs']['webhookData']['body']; value=body.get('value')
            valid=isinstance(value,(int,float)) and not isinstance(value,bool)
            answer=({'request_id':body['request_id'],'status':'ok','result':value*2} if valid else
                    {'request_id':body['request_id'],'status':'invalid','error':'invalid_input'})
            execution_id='mock-execution-'+str(len(self.remote));self.executions[execution_id]=answer
            return result({'executionId':execution_id,'status':'started'})
        if tool=='get_workflow_execution':
            return result({'execution':{'id':args['executionId'],'workflowId':self.workflow['id'],'status':'success','mode':'manual'},
                'data':{'resultData':{'lastNodeExecuted':'QA Response','runData':{'QA Response':[{'data':{'main':[[{'json':self.executions[args['executionId']]}]]}}]}}}})
        raise AssertionError('Unexpected remote operation '+tool)


class N8nPipelineTests(unittest.TestCase):
    def test_mismatched_remote_identity_blocks_before_execution_and_checkpoint(self):
        class WrongIdentity(PilotBackend):
            def mcp(self,**kwargs):
                raw=super().mcp(**kwargs)
                if kwargs['request']['tool']=='get_workflow_details':
                    return result({'workflow':{**self.workflow,'id':'different-resource'}})
                return raw
        with tempfile.TemporaryDirectory() as tmp:
            backend=WrongIdentity();core=N8nPipeline(Path(tmp),backend=backend)
            pid=core.create_qa_project(project_id='pilot-mismatch');report=core.run_pipeline(pid,stop_after=1)
            self.assertEqual(report['stage'],'BLOCKED');self.assertEqual(report['checkpoints'],[])
            self.assertFalse(any(r['tool'] in ('execute_workflow','publish_workflow') for r in backend.remote))

    def test_async_execution_is_polled_without_reexecuting(self):
        class AsyncBackend(PilotBackend):
            def mcp(self,**kwargs):
                tool=kwargs['request']['tool']
                if tool=='get_workflow_execution' and not getattr(self,'pending_seen',False):
                    self.pending_seen=True;self.remote.append(kwargs['request'])
                    return result({'execution':{'id':kwargs['request']['arguments']['executionId'],'workflowId':self.workflow['id'],'status':'running'}})
                return super().mcp(**kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            backend=AsyncBackend(); core=N8nPipeline(Path(tmp),backend=backend)
            pid=core.create_qa_project(project_id='pilot-async')
            report=core.run_pipeline(pid,stop_after=1)
            self.assertEqual(report['verified_increments'],1,report['blocker'])
            self.assertEqual(sum(r['tool']=='execute_workflow' for r in backend.remote),2)
            self.assertEqual(sum(r['tool']=='get_workflow_execution' for r in backend.remote),3)

    def test_matching_intermediate_data_cannot_approve_failed_or_running_execution(self):
        from athis_autopilot.n8n_pipeline import final_execution_output
        answer={'request_id':'pello-3b-unit','status':'ok','result':42}
        for status in ('running','error','success'):
            data={'execution':{'id':'e1','workflowId':'w1','status':status},'data':{'resultData':{
                'lastNodeExecuted':'QA Result','runData':{'QA Result':[{'data':{'main':[[{'json':answer}]]}}]}}}}
            with self.subTest(status=status):
                if status=='error':
                    with self.assertRaises(CodexBlocked):final_execution_output(data,'w1','e1')
                else:self.assertIsNone(final_execution_output(data,'w1','e1'))

    def test_draft_uses_existing_pipeline_and_persists_actual_resource_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend=PilotBackend(); core=N8nPipeline(Path(tmp),backend=backend)
            pid=core.create_qa_project(project_id='pilot-test')
            report=core.run_pipeline(pid,stop_after=1)
            self.assertEqual(report['stage'],'PAUSED',report['blocker'])
            self.assertEqual(report['verified_increments'],1)
            self.assertEqual(report['workflow_id'],'mock-owned-workflow')
            self.assertEqual(report['external_integration'],'TESTED WITH MOCKS')
            self.assertEqual(len(report['checkpoints']),1)
            self.assertEqual({s['role'] for s in report['sessions']},{'planner','executor','reviewer'})
            self.assertEqual(sum(r['tool']=='create_workflow_from_code' for r in backend.remote),1)
            self.assertTrue(core.journal.resource(pid)['reviewed_version'])
            self.assertFalse(any(r['tool']=='publish_workflow' for r in backend.remote))

    def test_unexpected_auto_credentials_block_before_execute_or_publish(self):
        with tempfile.TemporaryDirectory() as tmp:
            backend=PilotBackend(); backend.credentials=True
            core=N8nPipeline(Path(tmp),backend=backend); pid=core.create_qa_project(project_id='pilot-test')
            report=core.run_pipeline(pid,stop_after=1)
            self.assertFalse(report['passed']); self.assertEqual(report['stage'],'BLOCKED')
            self.assertEqual(report['checkpoints'],[])
            self.assertFalse(any(r['tool'] in ('execute_workflow','publish_workflow') for r in backend.remote))
