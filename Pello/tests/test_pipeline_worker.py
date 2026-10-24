import json
import os
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from pipeline_support import fixture
from athis_autopilot.codex_worker import main


class PipelineWorkerTests(unittest.TestCase):
    def test_reviewer_is_read_only_and_selected_model_is_passed_per_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, _ = fixture(tmp)
            folder = core.folder(pid); prompt = folder / 'prompt.txt'; prompt.write_text('Injected review')
            captured = {}
            class Thread:
                id = 'injected-supervisor-thread'
                def run(self, prompt, **options):
                    captured['turn'] = options
                    return SimpleNamespace(status='completed', id='injected-turn', usage=None, final_response='{}', error=None)
            class Client:
                def __init__(self, config): pass
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def account(self): return SimpleNamespace(account=SimpleNamespace(root=SimpleNamespace(type='chatgpt')))
                def models(self): return SimpleNamespace(data=[SimpleNamespace(model='gpt-6.1-sol', supported_reasoning_efforts=[SimpleNamespace(reasoning_effort=SimpleNamespace(value='high'))])])
                def thread_start(self, **options): captured['thread'] = options; return Thread()
            argv = ['--workspace', str(folder / 'workspace'), '--prompt', str(prompt),
                    '--thread-file', str(folder / 'supervisor-thread.txt'), '--result', str(folder / 'result.json'),
                    '--role', 'supervisor', '--model', 'gpt-6.1-sol', '--effort', 'high',
                    '--session-db', str(core.db_path), '--project-id', pid]
            with patch.dict(os.environ, {'CODEX_HOME': tmp}), patch('openai_codex.Codex', Client):
                self.assertEqual(main(argv), 0)
            self.assertEqual(captured['thread']['sandbox'].value, 'read-only')
            self.assertEqual(captured['thread']['approval_mode'].value, 'deny_all')
            self.assertEqual(captured['turn']['model'], 'gpt-6.1-sol')
            self.assertEqual(captured['turn']['effort'].value, 'high')
