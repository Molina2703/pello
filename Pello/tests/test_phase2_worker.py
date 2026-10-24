import os
from pathlib import Path
import tempfile
import unittest
import json
import sqlite3
from types import SimpleNamespace
from unittest.mock import patch
from athis_autopilot.codex_worker import restricted_overrides, main
from phase2_support import make_project


class WorkerConfigurationTests(unittest.TestCase):
    def test_inherited_mcp_servers_disabled_with_cli_key_syntax(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'config.toml').write_text('[mcp_servers.node_repl]\ncommand="unused"\n[mcp_servers.other-server]\ncommand="unused"\n')
            with patch.dict(os.environ, {'CODEX_HOME': tmp}):
                overrides = restricted_overrides()
            self.assertIn('mcp_servers.node_repl.enabled=false', overrides)
            self.assertIn('mcp_servers.other-server.enabled=false', overrides)
            self.assertFalse(any('mcp_servers."' in item for item in overrides))
            self.assertIn('sandbox_workspace_write.writable_roots=[]', overrides)
            self.assertIn('features.apps=false', overrides)

    def test_unrepresentable_mcp_name_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'config.toml').write_text('[mcp_servers."name.with.dots"]\ncommand="unused"\n')
            with patch.dict(os.environ, {'CODEX_HOME': tmp}), self.assertRaises(ValueError):
                restricted_overrides()

    def run_worker_fixture(self, resume, cached=False):
        with tempfile.TemporaryDirectory() as tmp:
            cycle, project_id, _ = make_project(tmp)
            folder = cycle.folder(project_id)
            prompt = folder / 'prompt.txt'; prompt.write_text('test only')
            result = folder / 'result.json'
            thread_file = folder / 'supervisor-thread.txt'
            events = []
            class FakeThread:
                id = 'injected-sdk-thread'
                def run(self, prompt, **options):
                    # A real session ID must already be durable when inference starts.
                    with cycle.db() as cx:
                        row = cx.execute('SELECT thread_id,status FROM pello_sessions WHERE project_id=? AND role=?', (project_id, 'supervisor')).fetchone()
                    assert tuple(row) == (self.id, 'IN_FLIGHT')
                    events.append('run')
                    return SimpleNamespace(status='completed', usage=None, id='injected-turn',
                                           final_response='{}', error=None)
            class FakeCodex:
                def __init__(self, config): pass
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def account(self): return SimpleNamespace(account=SimpleNamespace(root=SimpleNamespace(type='chatgpt')))
                def thread_start(self, **options):
                    assert options['sandbox'].value == 'read-only'
                    events.append('start'); return FakeThread()
                def thread_resume(self, thread_id, **options):
                    assert thread_id == FakeThread.id
                    events.append('resume'); return FakeThread()
            argv = ['worker', '--workspace', str(folder / 'workspace'), '--prompt', str(prompt),
                    '--thread-file', str(thread_file), '--result', str(result), '--role', 'supervisor',
                    '--session-db', str(cycle.db_path), '--project-id', project_id]
            with patch.dict(os.environ, {'CODEX_HOME': tmp}), patch('openai_codex.Codex', FakeCodex), patch('sys.argv', argv):
                shared = {'client': FakeCodex(None), 'thread_cache': {}} if cached else {}
                self.assertEqual(main(**shared), 0)
                if resume:
                    self.assertEqual(main(**shared), 0)
            expected = ['start', 'run', 'run'] if cached else (['start', 'run', 'resume', 'run'] if resume else ['start', 'run'])
            self.assertEqual(events, expected)
            self.assertEqual(json.loads(result.read_text())['thread_id'], FakeThread.id)
            self.assertTrue((folder / 'model-turn-submitted.json').exists())

    def test_fresh_thread_is_persisted_and_run_in_same_worker(self):
        self.run_worker_fixture(resume=False)

    def test_existing_thread_is_resumed_without_replacement(self):
        self.run_worker_fixture(resume=True)

    def test_review_reuses_handle_in_same_sdk_process(self):
        self.run_worker_fixture(resume=True, cached=True)
