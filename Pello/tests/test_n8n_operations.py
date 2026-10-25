"""Injected transport, real SQLite. No real n8n operations in this suite."""
import json
from pathlib import Path
import tempfile
import unittest

from pipeline_support import fixture, PipelineBackend
from athis_autopilot.engines import CodexBlocked
from athis_autopilot.n8n_operations import N8nJournal, claim_operation, finish_operation


def result(data):
    return {'status':'completed','thread_id':'injected-transport','result':{'isError':False,'structuredContent':data,'content':[]}}


class Transport(PipelineBackend):
    def __init__(self):
        super().__init__(); self.remote=[]; self.timeout=False; self.ambiguous=False; self.name=''
    def mcp(self, **kwargs):
        r=kwargs['request']; self.remote.append(r)
        if r['tool']=='validate_workflow': return result({'valid':True,'nodeCount':3})
        if r['tool']=='create_workflow_from_code':
            if self.timeout: raise TimeoutError('Injected uncertain creation')
            return result({'workflowId':'qa-own-1','name':self.name})
        if r['tool']=='search_workflows':
            values=[{'id':'qa-own-1','name':self.name}]
            if self.ambiguous: values.append({'id':'qa-own-2','name':self.name})
            return result({'data':values,'count':len(values)})
        return result({'success':True})


class ExternalOperationTests(unittest.TestCase):
    def setup_project(self, tmp, **limits):
        transport=Transport(); core,pid,_=fixture(tmp,backend=transport)
        journal=N8nJournal(core)
        transport.name='PELLO-3B-QA-injected-unique'
        journal.configure(pid,transport.name,'pello-3b-injected',**limits)
        return core,pid,journal,transport

    def create(self, journal, pid):
        journal.call(pid,'validate','validate_workflow',{'code':'approved fixture code'})
        return journal.call(pid,'create','create_workflow_from_code',{'code':'approved fixture code',
            'name':'PELLO-3B-QA-injected-unique','versionName':'Initial synthetic fixture'})

    def test_creation_id_is_persisted_and_confirmed_operations_are_not_repeated(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            first=self.create(journal,pid)
            self.assertEqual(journal.resource(pid)['workflow_id'],'qa-own-1')
            before=len(transport.remote)
            self.assertEqual(journal.call(pid,'create','create_workflow_from_code',{
                'code':'approved fixture code','name':transport.name,'versionName':'Initial synthetic fixture'}),first)
            self.assertEqual(len(transport.remote),before)
            self.assertEqual(journal.operations(pid)[-1]['status'],'CONFIRMED')

    def test_uncertain_create_never_blindly_retries_and_reconciles_by_unique_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp); transport.timeout=True
            with self.assertRaises(CodexBlocked): self.create(journal,pid)
            self.assertEqual(journal.operations(pid)[-1]['status'],'UNCERTAIN')
            calls=len(transport.remote)
            with self.assertRaises(CodexBlocked): self.create(journal,pid)
            self.assertEqual(len(transport.remote),calls)
            journal.reconcile_create(pid,'create')
            self.assertEqual(journal.resource(pid)['workflow_id'],'qa-own-1')
            self.assertEqual(journal.operations(pid)[1]['status'],'CONFIRMED')
            self.assertEqual(sum(r['tool']=='create_workflow_from_code' for r in transport.remote),1)

    def test_ambiguous_creation_stays_uncertain_and_blocks_more_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp); transport.timeout=True; transport.ambiguous=True
            with self.assertRaises(CodexBlocked): self.create(journal,pid)
            with self.assertRaises(CodexBlocked): journal.reconcile_create(pid,'create')
            with self.assertRaises(CodexBlocked): journal.call(pid,'create-again','create_workflow_from_code',
                {'code':'approved fixture code','name':transport.name,'versionName':'Second'})
            self.assertIsNone(journal.resource(pid)['workflow_id'])

    def test_stop_blocks_new_operations_without_disabling_any_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            (core.folder(pid)/'STOP').write_text('User emergency stop')
            with self.assertRaises(CodexBlocked): journal.call(pid,'read','search_workflows',{'query':transport.name})
            self.assertEqual(transport.remote,[])

    def test_scope_secrets_and_unreviewed_publication_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            for tool,args in [('get_workflow_details',{'workflowId':'dFoCUpXVrP9gc9rY'}),
                              ('get_workflow_details',{'workflowId':'I4qwL8MuXvTotZKU'}),
                              ('search_workflows',{'query':'customer'}),
                              ('list_credentials',{}),('publish_workflow',{'workflowId':'unknown'}),
                              ('validate_workflow',{'code':'test','api_key':'sensitive-value'})]:
                with self.subTest(tool=tool,args=args),self.assertRaises(CodexBlocked): journal.call(pid,tool,tool,args)
            self.assertEqual(transport.remote,[])
            self.create(journal,pid)
            with self.assertRaises(CodexBlocked): journal.call(pid,'publish','publish_workflow',{'workflowId':'qa-own-1','versionId':'v1'})
            with self.assertRaises(CodexBlocked): journal.reviewed(pid,'v1','hash',tests_passed=False,review_passed=True)

    def test_limits_do_not_grant_more_budget_and_changed_intent_cannot_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp,max_calls=1)
            journal.call(pid,'read','search_workflows',{'query':transport.name})
            with self.assertRaises(CodexBlocked): journal.call(pid,'next','search_workflows',{'query':transport.name})
            with self.assertRaises(CodexBlocked): journal.call(pid,'read','search_workflows',{'query':transport.name,'limit':1})
            self.assertEqual(len(transport.remote),1)

    def test_native_submission_claim_is_atomic_and_records_id_before_return(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            journal.call(pid,'validate','validate_workflow',{'code':'approved fixture code'})
            args={'code':'approved fixture code','name':transport.name,'versionName':'Initial'}
            journal.prepare(pid,'create','create_workflow_from_code',args)
            proof={'db':str(core.db_path),'project_id':pid,'key':'create'}
            claim_operation(proof,'create_workflow_from_code',args,'native-thread')
            self.assertEqual(journal.operations(pid)[-1]['status'],'SUBMITTED')
            with self.assertRaises(CodexBlocked): claim_operation(proof,'create_workflow_from_code',args,'another-thread')
            finish_operation(proof,result({'workflowId':'qa-own-1'})['result'])
            self.assertEqual(journal.resource(pid)['workflow_id'],'qa-own-1')
            self.assertEqual(journal.operations(pid)[-1]['status'],'CONFIRMED')

    def test_mutation_and_time_budgets_cannot_be_extended_by_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp,max_mutations=1)
            self.create(journal,pid)
            journal.reviewed(pid,'v1','known-synthetic-hash',tests_passed=True,review_passed=True)
            with self.assertRaises(CodexBlocked): journal.call(pid,'publish','publish_workflow',{'workflowId':'qa-own-1','versionId':'v1'})
            original=journal.resource(pid)['deadline']
            journal.configure(pid,transport.name,'pello-3b-injected',max_mutations=1,seconds=3600)
            self.assertEqual(journal.resource(pid)['deadline'],original)
            with core.db() as cx: cx.execute('UPDATE pello_n8n_projects SET deadline=0 WHERE project_id=?',(pid,))
            with self.assertRaises(CodexBlocked): journal.call(pid,'read','search_workflows',{'query':transport.name})

    def test_native_worker_persists_creation_before_returning_to_core(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from athis_autopilot.n8n_mcp import worker_request
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            journal.call(pid,'validate','validate_workflow',{'code':'approved fixture code'})
            args={'code':'approved fixture code','name':transport.name,'versionName':'Initial'}
            journal.prepare(pid,'create','create_workflow_from_code',args)
            captured={}
            class RPC:
                def request(self, method, parameters, **kwargs):
                    self_test.assertEqual(journal.operations(pid)[-1]['status'],'SUBMITTED')
                    self_test.assertEqual(parameters['tool'],'create_workflow_from_code')
                    return SimpleNamespace(model_dump=lambda **_:result({'workflowId':'qa-own-1'})['result'])
            class Client:
                _client=RPC()
                def thread_start(self, **kwargs):
                    captured.update(kwargs); return SimpleNamespace(id='injected-native-executor')
            self_test=self
            with patch('athis_autopilot.n8n_mcp.connection_summary',return_value={}):
                response=worker_request(Client(),role='executor',workspace=core.folder(pid)/'workspace',
                    request={'action':'call','tool':'create_workflow_from_code','arguments':args,
                        'operation':{'db':str(core.db_path),'project_id':pid,'key':'create'}})
            self.assertEqual(journal.resource(pid)['workflow_id'],'qa-own-1')
            self.assertEqual(journal.operations(pid)[-1]['status'],'CONFIRMED')
            self.assertEqual(captured['config']['mcp_servers.n8n.enabled_tools'],['create_workflow_from_code'])

    def test_resource_reads_require_workflow_scope_and_known_execution_ownership(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            self.create(journal,pid)
            cases=[('get_execution',{'executionId':'foreign'}),
                   ('get_workflow_details',{}),('get_workflow_history',{}),
                   ('get_workflow_execution',{'executionId':'foreign'}),
                   ('search_workflow_executions',{}),
                   ('get_workflow_execution',{'workflowId':'qa-own-1','executionId':'foreign'})]
            for index,(tool,args) in enumerate(cases):
                with self.subTest(tool=tool,args=args),self.assertRaises(CodexBlocked):
                    journal.call(pid,'foreign-read-'+str(index),tool,args)

    def test_execution_ids_from_owned_execution_results_allow_scoped_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            core,pid,journal,transport=self.setup_project(tmp)
            self.create(journal,pid)
            original=transport.mcp
            def execute(**kwargs):
                if kwargs['request']['tool']=='execute_workflow':
                    return result({'executionId':'own-execution','workflowId':'qa-own-1'})
                return original(**kwargs)
            transport.mcp=execute
            journal.call(pid,'execute','execute_workflow',{'workflowId':'qa-own-1','executionMode':'manual'})
            response=journal.call(pid,'read-execution','get_workflow_execution',{'workflowId':'qa-own-1','executionId':'own-execution'})
            self.assertTrue(response['structuredContent']['success'])
