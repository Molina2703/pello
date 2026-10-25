"""Publication/HTTP failures are simulated; never evidence of a live webhook."""
import json
from pathlib import Path
import tempfile
import unittest
from test_n8n_pipeline import PilotBackend
from test_n8n_operations import result
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.n8n_pipeline import N8nPipeline
from athis_autopilot.n8n_mcp import redact_result


class PublishBackend(PilotBackend):
    def __init__(self): super().__init__();self.http_calls=[];self.webhook_cases={};self.drift=False
    def run(self,**kwargs):
        if 'PIPELINE CONTEXT (JSON):\n' in kwargs['prompt'] and kwargs['out_dir'].name=='execute':
            data=json.loads(kwargs['prompt'].split('PIPELINE CONTEXT (JSON):\n')[1])
            if data['current_increment']['owner']['task_id']=='PUBLISH':
                thread=kwargs['thread_file'];r=data['n8n_resource']
                (kwargs['workspace']/'publication.json').write_text(json.dumps({'action':'publish','workflow_id':r['workflow_id'],'version_id':r['reviewed_version']}))
                raw={'status':'completed','thread_id':thread.read_text(),'turn_id':'mock-publish-turn',
                    'final_response':json.dumps({'project_id':data['project_id'],'task_id':'PUBLISH','execution_summary':'Injected publication intent',
                    'files_modified':['publication.json'],'errors':[],'evidence_paths':[]})}
                kwargs['out_dir'].mkdir(parents=True);(kwargs['out_dir']/'codex_result.json').write_text(json.dumps(raw));return raw
        return super().run(**kwargs)
    def mcp(self,**kwargs):
        req=kwargs['request'];tool=req['tool'];args=req['arguments']
        if tool=='publish_workflow':
            self.remote.append(req);self.workflow['active']=True;self.workflow['activeVersionId']=args['versionId']
            return result({'success':True,'workflowId':self.workflow['id'],'activeVersionId':args['versionId']})
        if tool=='get_workflow_details' and self.drift:
            self.remote.append(req);return result({'workflow':{**self.workflow,'versionId':'unreviewed-change'}})
        if tool=='search_workflow_executions':
            self.remote.append(req);return result({'data':[{'id':eid,'workflowId':self.workflow['id'],'mode':'webhook','status':'success'} for eid in self.webhook_cases]})
        if tool=='get_workflow_execution' and args['executionId'] in self.webhook_cases:
            self.remote.append(req);case=self.webhook_cases[args['executionId']]
            return result({'execution':{'id':args['executionId'],'workflowId':self.workflow['id'],'mode':'webhook','status':'success'},
                'data':{'resultData':{'lastNodeExecuted':'QA Response','runData':{
                    'QA Webhook':[{'data':{'main':[[{'json':{'body':case['payload']}}]]}}],
                    'QA Response':[{'data':{'main':[[{'json':case['body']}]]}}]}}}})
        return super().mcp(**kwargs)
    def http(self,path,payload):
        self.http_calls.append((path,payload));value=payload.get('value');valid=isinstance(value,(int,float)) and not isinstance(value,bool)
        body=({'request_id':payload['request_id'],'status':'ok','result':value*2} if valid else
            {'request_id':payload['request_id'],'status':'invalid','error':'invalid_input'})
        self.webhook_cases['mock-http-'+str(len(self.http_calls))]={'payload':payload,'body':body}
        return {'status':200 if valid else 400,'body':body}


class PublicationTests(unittest.TestCase):
    def draft(self,tmp):
        backend=PublishBackend();core=N8nPipeline(Path(tmp),backend=backend,http_transport=backend.http)
        pid=core.create_qa_project(project_id='publish-qa');report=core.run_pipeline(pid,stop_after=1)
        self.assertEqual(report['verified_increments'],1,report['blocker']);return core,pid,backend

    def test_mock_published_pipeline_verifies_http_executions_and_resume_has_no_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp);report=core.run_pipeline(pid)
            self.assertTrue(report['passed'],report['blocker']);self.assertEqual(len(report['checkpoints']),2)
            self.assertEqual(report['external_integration'],'TESTED WITH MOCKS');self.assertEqual(len(backend.http_calls),4)
            before=(len(backend.remote),len(backend.http_calls));self.assertTrue(core.run_pipeline(pid)['passed'])
            self.assertEqual(before,(len(backend.remote),len(backend.http_calls)))

    def test_budget_exhaustion_blocks_before_publish_coder_or_any_remote_effect(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp)
            # Simulate reaching the immutable initial maximum; production never changes it.
            with core.db() as cx:cx.execute('UPDATE pello_n8n_projects SET max_mutations=3 WHERE project_id=?',(pid,))
            before=len(backend.remote);report=core.run_pipeline(pid)
            self.assertEqual(report['stage'],'BLOCKED');self.assertIn('budget',report['blocker'].lower())
            self.assertEqual(len(backend.remote),before);self.assertEqual(backend.http_calls,[])
            self.assertFalse((core.folder(pid)/'workspace/publication.json').exists())

    def test_version_drift_blocks_publication_and_http(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp);backend.drift=True;report=core.run_pipeline(pid)
            self.assertEqual(report['stage'],'BLOCKED');self.assertEqual(backend.http_calls,[])
            self.assertFalse(any(r['tool']=='publish_workflow' for r in backend.remote))

    def test_http_uncertainty_stop_budget_and_scope_are_enforced_without_repetition(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp)
            r=core.journal.resource(pid);core.journal.call(pid,'publish','publish_workflow',{'workflowId':r['workflow_id'],'versionId':r['reviewed_version']})
            def uncertain(path,payload):raise TimeoutError('injected timeout after submission')
            core.http.transport=uncertain
            payload={'request_id':'pello-3b-valid','value':21,'op':'double'}
            with self.assertRaises(CodexBlocked):core.http.post(pid,'case-1',payload)
            core.http.transport=backend.http
            with self.assertRaises(CodexBlocked):core.http.post(pid,'case-1',payload)
            with self.assertRaises(CodexBlocked):core.http.post(pid,'case-2',payload)
            self.assertEqual(backend.http_calls,[])
            (core.folder(pid)/'STOP').write_text('stop')
            with self.assertRaises(CodexBlocked):core.http.post(pid,'case-3',payload)

    def test_internal_execution_tokens_are_redacted_in_both_mcp_representations(self):
        raw={'structuredContent':{'data':{'resumeToken':'synthetic-private-token'}},
             'content':[{'type':'text','text':json.dumps({'data':{'resumeToken':'synthetic-private-token'}})}]}
        cleaned=redact_result(raw)
        self.assertNotIn('synthetic-private-token',json.dumps(cleaned));self.assertIn('[REDACTED]',json.dumps(cleaned))

    def test_four_post_limit_confirmed_cache_and_scoped_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp);r=core.journal.resource(pid)
            payload={'request_id':'pello-3b-valid','value':21,'op':'double'}
            with self.assertRaises(CodexBlocked):core.http.post(pid,'unpublished',payload)
            core.journal.call(pid,'publish','publish_workflow',{'workflowId':r['workflow_id'],'versionId':r['reviewed_version']})
            for i in range(4):core.http.post(pid,'case-'+str(i),payload)
            core.http.post(pid,'case-0',payload);self.assertEqual(len(backend.http_calls),4)
            with self.assertRaises(CodexBlocked):core.http.post(pid,'fifth',payload)
            with self.assertRaises(CodexBlocked):core.http.post(pid,'foreign',{**payload,'request_id':'customer-1'})
