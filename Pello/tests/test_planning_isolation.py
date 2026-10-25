"""Planning roles must lose reading tools, not merely write permission."""
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from athis_autopilot.codex_worker import main


DENIED = ('shell_tool', 'unified_exec', 'view_image', 'code_mode', 'code_mode_host',
          'browser_use', 'computer_use', 'in_app_browser', 'image_generation',
          'artifact', 'apps', 'plugins', 'multi_agent', 'multi_agent_v2',
          'skill_search', 'memories')


class PlanningIsolationTests(unittest.TestCase):
    def invoke(self, role, resume=False):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); seen = {}
            (root / 'prompt').write_text('Synthetic supplied context only.')
            if resume: (root / 'thread').write_text('existing')
            class Thread:
                id = 'existing'
                def run(self, prompt, **kwargs):
                    return SimpleNamespace(status='completed', usage=None, id='turn',
                                           final_response='{}', error=None)
            class Client:
                def account(self):
                    return SimpleNamespace(account=SimpleNamespace(root=SimpleNamespace(type='chatgpt')))
                def thread_start(self, **kwargs): seen.update(kwargs); return Thread()
                def thread_resume(self, identity, **kwargs): seen.update(kwargs); return Thread()
            with patch.dict(os.environ, {'CODEX_HOME': tmp}):
                main(['--workspace', str(root), '--prompt', str(root/'prompt'),
                      '--thread-file', str(root/'thread'), '--result', str(root/'result'),
                      '--role', role], client=Client())
            return seen, json.loads((root/'model-turn-submitted.json').read_text())

    def test_all_read_only_roles_disable_every_reading_surface(self):
        for role in ('planner', 'reviewer', 'tester', 'supervisor'):
            with self.subTest(role=role):
                options, receipt = self.invoke(role)
                config = options.get('config', {})
                for name in DENIED:
                    self.assertIs(config.get('features.'+name), False, name)
                self.assertEqual(config.get('web_search'), 'disabled')
                self.assertTrue(config.get('features.skip_host_skill_discovery'))
                self.assertEqual(config.get('project_doc_max_bytes'), 0)
                self.assertEqual(receipt.get('context_isolation'), config)

    def test_resume_reapplies_restrictions(self):
        options, receipt = self.invoke('planner', resume=True)
        self.assertIs(options.get('config', {}).get('features.shell_tool'), False)
        self.assertEqual(receipt.get('context_isolation'), options['config'])

    def test_executor_keeps_existing_implementation_tools(self):
        options, receipt = self.invoke('executor')
        self.assertNotIn('config', options)
        self.assertEqual(options['sandbox'].value, 'workspace-write')
        self.assertIsNone(receipt.get('context_isolation'))
