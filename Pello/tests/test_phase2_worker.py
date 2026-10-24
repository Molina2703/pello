import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from athis_autopilot.codex_worker import restricted_overrides


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
