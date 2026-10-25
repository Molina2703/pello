"""Deterministic MCP transport tests. Fake SDK, never real integration evidence."""
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from athis_autopilot.n8n_mcp import ENDPOINT, executor_config, worker_request
from athis_autopilot.codex_worker import restricted_overrides


class N8nPreflightTests(unittest.TestCase):
    def test_connection_profile_keeps_other_servers_disabled_and_role_scoped(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'config.toml').write_text('[mcp_servers.n8n]\nurl=' + json.dumps(ENDPOINT) +
                '\n[mcp_servers.other]\ncommand="unused"\n', encoding='utf-8')
            with patch.dict(os.environ, {'CODEX_HOME': tmp}):
                base = restricted_overrides()
                profile = executor_config('executor', {'search_workflows'})
                self.assertIn('mcp_servers.other.enabled=false', base)
                self.assertIn('mcp_servers.n8n.enabled=false', base)
                self.assertTrue(profile['mcp_servers.n8n.enabled'])
                self.assertEqual(profile['mcp_servers.n8n.enabled_tools'], ['search_workflows'])
                for role in ('planner', 'reviewer', 'tester', 'supervisor'):
                    with self.subTest(role=role), self.assertRaises(ValueError): executor_config(role)

    def test_wrong_endpoint_and_mutation_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, 'config.toml').write_text('[mcp_servers.n8n]\nurl="https://other.invalid/mcp"\n')
            with patch.dict(os.environ, {'CODEX_HOME': tmp}), self.assertRaises(ValueError): executor_config('executor')
        with self.assertRaises(ValueError): worker_request(None, role='executor', workspace=Path('.'),
            request={'action':'call','tool':'publish_workflow','arguments':{'workflowId':'protected'}})

    def test_native_sdk_rpc_uses_executor_thread_and_exact_safe_arguments(self):
        captures = {}
        class RPC:
            def request(self, method, args, **kwargs):
                captures.update(method=method, args=args)
                return SimpleNamespace(model_dump=lambda **_: {'content':[], 'isError':False})
        class Client:
            _client = RPC()
            def thread_start(self, **kwargs):
                captures['thread'] = kwargs
                return SimpleNamespace(id='injected-mcp-thread')
        with patch('athis_autopilot.n8n_mcp.connection_summary', return_value={}):
            result = worker_request(Client(), role='executor', workspace=Path('.'),
                request={'action':'call','tool':'search_workflows','arguments':{'query':'PELLO-3B-QA'}})
        self.assertEqual(captures['method'], 'mcpServer/tool/call')
        from openai_codex.generated.v2_all import McpServerToolCallRequest
        McpServerToolCallRequest.model_validate({'id':'test', 'method':captures['method'], 'params':captures['args']})
        self.assertEqual(captures['args']['server'], 'n8n')
        self.assertEqual(captures['args']['threadId'], 'injected-mcp-thread')
        self.assertEqual(captures['thread']['sandbox'].value, 'read-only')
        self.assertFalse(result['model_inference'])

    def test_protected_workflows_and_unscoped_search_are_rejected_before_rpc(self):
        for request in ({'action':'call','tool':'get_workflow_details','arguments':{'workflowId':'dFoCUpXVrP9gc9rY'}},
                        {'action':'call','tool':'get_workflow_details','arguments':{'workflowId':'foreign'}},
                        {'action':'call','tool':'search_workflows','arguments':{}}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                worker_request(None, role='executor', workspace=Path('.'), request=request)
