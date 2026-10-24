import json
import os
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from pipeline_support import fixture
from athis_autopilot.codex_worker import main
from athis_autopilot.ai_supervisor import ROLE_INSTRUCTIONS
from athis_autopilot.pipeline_contracts import PipelinePolicy


class PipelineWorkerTests(unittest.TestCase):
    def test_all_role_profiles_and_permissions_are_transmitted_to_sdk(self):
        with tempfile.TemporaryDirectory() as tmp:
            from pathlib import Path
            root = Path(tmp); captured = []
            class Thread:
                def __init__(self, identity): self.id = identity
                def run(self, prompt, **options):
                    captured[-1]['turn'] = options
                    return SimpleNamespace(status='completed', id='injected-turn', usage=None, final_response='{}', error=None)
            class Client:
                def __init__(self, config): pass
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def account(self): return SimpleNamespace(account=SimpleNamespace(root=SimpleNamespace(type='chatgpt')))
                def models(self):
                    return SimpleNamespace(data=[SimpleNamespace(model=model, supported_reasoning_efforts=[
                        SimpleNamespace(reasoning_effort=SimpleNamespace(value=effort)) for effort in ('low','medium','high')])
                        for model in ('gpt-6.1-sol','gpt-6-luna')])
                def thread_start(self, **options):
                    captured.append({'thread': options}); return Thread('injected-role-' + str(len(captured)))
            policy = PipelinePolicy()
            for role, profile in policy.role_profiles.items():
                worker_role = 'executor' if role == 'coder' else role
                prompt = root / 'prompt.txt'; prompt.write_text('Injected role fixture')
                instructions = root / 'instructions.txt'; instructions.write_text(ROLE_INSTRUCTIONS[worker_role])
                argv = ['--workspace', str(root), '--prompt', str(prompt), '--thread-file', str(root / (role + '.thread')),
                        '--result', str(root / 'result.json'), '--role', worker_role, '--instructions', str(instructions),
                        '--model', profile.model, '--effort', profile.effort]
                with self.subTest(role=role), patch.dict(os.environ, {'CODEX_HOME': tmp}), patch('openai_codex.Codex', Client):
                    self.assertEqual(main(argv), 0)
                self.assertEqual(captured[-1]['thread']['model'], profile.model)
                self.assertEqual(captured[-1]['turn']['model'], profile.model)
                self.assertEqual(captured[-1]['turn']['effort'].value, profile.effort)
                self.assertEqual(captured[-1]['thread']['developer_instructions'], ROLE_INSTRUCTIONS[worker_role])
                self.assertEqual(captured[-1]['thread']['sandbox'].value, 'workspace-write' if role == 'coder' else 'read-only')
                self.assertEqual(captured[-1]['thread']['approval_mode'].value, 'deny_all')
                submission = json.loads((root / 'model-turn-submitted.json').read_text())
                self.assertEqual((submission['model'], submission['effort']), (profile.model, profile.effort))
                self.assertEqual(submission['sandbox'], captured[-1]['thread']['sandbox'].value)

    def test_reviewer_is_read_only_and_selected_model_is_passed_per_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, _ = fixture(tmp)
            folder = core.folder(pid); prompt = folder / 'prompt.txt'; prompt.write_text('Injected review')
            captured = {}
            class Thread:
                id = 'injected-reviewer-thread'
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
                    '--thread-file', str(folder / 'reviewer-thread.txt'), '--result', str(folder / 'result.json'),
                    '--role', 'reviewer', '--model', 'gpt-6.1-sol', '--effort', 'high',
                    '--session-db', str(core.db_path), '--project-id', pid]
            with patch.dict(os.environ, {'CODEX_HOME': tmp}), patch('openai_codex.Codex', Client):
                self.assertEqual(main(argv), 0)
            self.assertEqual(captured['thread']['sandbox'].value, 'read-only')
            self.assertEqual(captured['thread']['approval_mode'].value, 'deny_all')
            self.assertEqual(captured['turn']['model'], 'gpt-6.1-sol')
            self.assertEqual(captured['turn']['effort'].value, 'high')
