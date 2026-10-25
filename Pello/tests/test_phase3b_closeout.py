"""Closeout control tests. Models, MCP and HTTP are injected, not live evidence."""
import json
from pathlib import Path
import tempfile
import time
import unittest
from test_n8n_publication import PublishBackend
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.n8n_pipeline import N8nPipeline

AUTH={'authorization_id':'user-phase3b3-completion-20261024','workflow_id':'Tbuvwcxde8MEMYcJ',
      'cumulative_mutations':14,'additional_mutations':8,'http_posts':4,'deadline_extension_seconds':5400,
      'source':'Explicit human request: PELLO — PHASE 3B.3 COMPLETION, section 4'}


class CloseoutTests(unittest.TestCase):
    def test_identical_valid_requests_are_correlated_in_execution_time_order(self):
        class NewestFirst(PublishBackend):
            def mcp(self,**kwargs):
                raw=super().mcp(**kwargs)
                if kwargs['request']['tool']=='search_workflow_executions':
                    from athis_autopilot.n8n_operations import mcp_data
                    rows=mcp_data(raw)['data']
                    for i,row in enumerate(rows):row['startedAt']=f'2026-10-25T05:00:0{i}.000Z'
                    raw['result']['structuredContent']['data']=list(reversed(rows))
                return raw
        with tempfile.TemporaryDirectory() as tmp:
            backend=NewestFirst();core=N8nPipeline(Path(tmp),backend=backend,http_transport=backend.http)
            pid=core.create_qa_project(project_id='closeout-order');self.assertTrue(core.run_pipeline(pid)['passed'])
            evidence=json.loads((core.folder(pid)/'workspace/remote-published.json').read_text())
            ids={r['case']:r['id'] for r in evidence['execution_results']}
            self.assertEqual(ids['valid'],'mock-http-1');self.assertEqual(ids['repeat-valid'],'mock-http-4')

    def test_staged_review_context_and_scoped_retry_preserve_final_protected_suite(self):
        class StrictReview(PublishBackend):
            def run(self,**kwargs):
                if 'closeout-publication' in kwargs['out_dir'].parts and kwargs['out_dir'].name=='review':
                    data=json.loads(kwargs['prompt'].split('PIPELINE CONTEXT (JSON):\n')[1]);owner=data['current_increment']['owner']
                    if owner['suite']!='draft' or owner['expected_tests']!=5:
                        raw={'status':'completed','thread_id':kwargs['thread_file'].read_text(),'turn_id':'injected-ambiguous-review',
                            'final_response':json.dumps({'project_id':data['project_id'],'task_id':'PUBLISH','attempt':1,'verdict':'BLOCKED',
                            'diagnosis':'infrastructure','feedback':'Published suite missing in the supplied stage contract'})}
                        kwargs['out_dir'].mkdir(parents=True,exist_ok=True);(kwargs['out_dir']/'codex_result.json').write_text(json.dumps(raw));return raw
                return super().run(**kwargs)
        class LegacyContext(N8nPipeline):
            def _call(self,project,phase,role,data,model_class,**kwargs):
                if phase=='closeout-publication/review':
                    data['current_increment']['owner'].update(suite='published',expected_tests=1)
                return super()._call(project,phase,role,data,model_class,**kwargs)
        with tempfile.TemporaryDirectory() as tmp:
            backend=StrictReview();core=LegacyContext(Path(tmp),backend=backend,http_transport=backend.http)
            pid=core.create_qa_project(project_id='closeout-context');core.run_pipeline(pid,stop_after=1)
            self.assertEqual(core.publish_increment(pid)['stage'],'BLOCKED')
            previous=core.operation(pid,'closeout-publication/review')
            restored=N8nPipeline(Path(tmp),backend=backend,http_transport=backend.http)
            result=restored.publish_increment(pid,review_round=2)
            self.assertEqual(result['stage'],'PAUSED',result['blocker']);self.assertEqual(previous,restored.operation(pid,'closeout-publication/review'))
            self.assertEqual(sum(r['tool']=='publish_workflow' for r in backend.remote),1);self.assertEqual(backend.http_calls,[])
            final=next(t for t in restored.manifest(pid).increments if t.task_id=='PUBLISH')
            self.assertEqual((final.suite,final.expected_tests),('published',1));restored._integrity(restored.project(pid))

    def test_fresh_instance_recovers_a_realistically_lost_publish_response(self):
        class LostResponse(PublishBackend):
            def mcp(self,**kwargs):
                value=super().mcp(**kwargs)
                if kwargs['request']['tool']=='publish_workflow':raise TimeoutError('response lost after remote activation')
                return value
        with tempfile.TemporaryDirectory() as tmp:
            backend=LostResponse();core=N8nPipeline(Path(tmp),backend=backend,http_transport=backend.http)
            pid=core.create_qa_project(project_id='closeout-lost');core.run_pipeline(pid,stop_after=1)
            first=core.publish_increment(pid);self.assertEqual(first['stage'],'BLOCKED')
            self.assertTrue(backend.workflow['active'])
            restored=N8nPipeline(Path(tmp),backend=backend,http_transport=backend.http)
            result=restored.publish_increment(pid)
            self.assertEqual(result['stage'],'PAUSED',result['blocker']);self.assertEqual(backend.http_calls,[])
            self.assertEqual(sum(r['tool']=='publish_workflow' for r in backend.remote),1)
            self.assertEqual(next(r for r in restored.journal.operations(pid) if r['op_key']=='publish')['status'],'CONFIRMED')

    def draft(self,tmp):
        backend=PublishBackend();core=N8nPipeline(Path(tmp),backend=backend,http_transport=backend.http)
        pid=core.create_qa_project(project_id='closeout-qa');self.assertEqual(core.run_pipeline(pid,stop_after=1)['verified_increments'],1)
        return core,pid,backend

    def test_explicit_authorization_is_scoped_idempotent_and_preserves_counters(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp)
            with self.assertRaises(CodexBlocked):core.journal.authorize_closeout(pid,AUTH)
            with core.db() as cx:
                cx.execute('UPDATE pello_n8n_projects SET workflow_id=?,deadline=? WHERE project_id=?',(AUTH['workflow_id'],time.time()-1,pid))
            before=core.journal.operations(pid)
            core.journal.authorize_closeout(pid,AUTH);first=core.journal.resource(pid)
            core.journal.authorize_closeout(pid,AUTH)
            self.assertEqual(core.journal.resource(pid),first);self.assertEqual(first['max_mutations'],14)
            self.assertGreater(first['deadline'],time.time());self.assertLessEqual(first['deadline'],time.time()+5400)
            self.assertEqual(core.journal.operations(pid),before)
            with self.assertRaises(CodexBlocked):core.journal.authorize_closeout(pid,{**AUTH,'cumulative_mutations':15})

    def test_publication_checkpoint_precedes_all_http_and_resume_finishes_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp);a=core.publish_increment(pid)
            self.assertEqual(a['stage'],'PAUSED',a['blocker']);self.assertEqual(backend.http_calls,[])
            proof=json.loads((core.folder(pid)/'evidence/closeout/publication.json').read_text())
            self.assertTrue(proof['workflow']['active']);self.assertEqual(proof['review']['verdict'],'PASS')
            self.assertEqual(sum(r['tool']=='publish_workflow' for r in backend.remote),1)
            b=core.run_pipeline(pid);self.assertTrue(b['passed'],b['blocker']);self.assertEqual(len(backend.http_calls),4)
            self.assertEqual(sum(r['tool']=='publish_workflow' for r in backend.remote),1)

    def test_already_published_reviewed_version_is_not_published_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp);backend.workflow['active']=True;backend.workflow['activeVersionId']='mock-v1'
            with core.db() as cx:cx.execute('UPDATE pello_n8n_projects SET max_mutations=3 WHERE project_id=?',(pid,))
            a=core.publish_increment(pid);self.assertEqual(a['stage'],'PAUSED',a['blocker'])
            self.assertFalse(any(r['tool']=='publish_workflow' for r in backend.remote))
            self.assertTrue(core.run_pipeline(pid)['passed']);self.assertEqual(len(backend.http_calls),4)
            self.assertFalse(any(r['tool']=='publish_workflow' for r in backend.remote))

    def test_uncertain_publish_is_reconciled_by_read_without_resubmission(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,backend=self.draft(tmp);r=core.journal.resource(pid)
            core.journal.prepare(pid,'publish','publish_workflow',{'workflowId':r['workflow_id'],'versionId':r['reviewed_version']})
            with core.db() as cx:cx.execute("UPDATE pello_n8n_operations SET status='UNCERTAIN' WHERE project_id=? AND op_key='publish'",(pid,))
            with core.db() as cx:cx.execute('UPDATE pello_n8n_projects SET max_mutations=4 WHERE project_id=?',(pid,))
            backend.workflow['active']=True;backend.workflow['activeVersionId']='mock-v1'
            a=core.publish_increment(pid);self.assertEqual(a['stage'],'PAUSED',a['blocker'])
            self.assertFalse(any(r['tool']=='publish_workflow' for r in backend.remote))
            op=next(r for r in core.journal.operations(pid) if r['op_key']=='publish');self.assertEqual(op['status'],'CONFIRMED')
