"""The blind boundary must select an enforced named profile, not legacy mode."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace
from athis_autopilot.codex_worker import main


class BlindPermissionTests(unittest.TestCase):
    def run_profile(self, reported='pello_supplied_context', role='planner'):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'prompt').write_text('Supplied context only')
            captured={}
            class Wire:
                def request(self, method, params, response_model):
                    captured.update(params)
                    return response_model.model_validate({'thread':{'id':'isolated'},
                        'activePermissionProfile':{'id':reported,'extends':':read-only'},
                        'sandbox':{'type':'readOnly','networkAccess':False},'instructionSources':[]})
            class Client:
                _client=Wire()
                def account(self):return SimpleNamespace(account=SimpleNamespace(root=SimpleNamespace(type='chatgpt')))
            argv=['--workspace',str(root),'--prompt',str(root/'prompt'),'--thread-file',str(root/'thread'),
                  '--result',str(root/'result'),'--role',role,'--deny-read-root',str(root/'hidden')]
            turn=SimpleNamespace(status='completed',usage=None,id='turn',final_response='{}',error=None)
            with patch('openai_codex.api.Thread.run',return_value=turn):
                main(argv,client=Client())
            return captured,json.loads((root/'model-turn-submitted.json').read_text())

    def test_named_read_deny_profile_is_selected_and_receipted(self):
        params,receipt=self.run_profile()
        self.assertNotIn('sandbox',params,'Legacy mode silently discards the named profile')
        cfg=params['config']
        self.assertEqual(cfg['default_permissions'],'pello_supplied_context')
        rules=cfg['permissions.pello_supplied_context']['filesystem']
        self.assertTrue(rules and all(v=='deny' for v in rules.values()))
        self.assertEqual(receipt['active_permission_profile']['id'],'pello_supplied_context')

    def test_missing_or_substituted_runtime_profile_blocks_before_inference(self):
        with self.assertRaisesRegex(ValueError,'permission profile'):
            self.run_profile(reported=':read-only')

    def test_denied_roots_cannot_silently_change_executor_permissions(self):
        with self.assertRaisesRegex(ValueError,'reasoning'):
            self.run_profile(role='executor')
