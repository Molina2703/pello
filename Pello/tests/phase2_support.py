"""Injected model responses for deterministic tests, never live SDK evidence."""
import json
from pathlib import Path

from athis_autopilot.supervised import SupervisedCycle


class FakeBackend:
    def __init__(self):
        self.calls = []
        self.preparations = []
        self.bad_phase = None
        self.wrong_phase = None
        self.failure = None
        self.crash_after_write = None
        self.bad_code = False
        self.review_action = 'COMPLETE'
        self.plan_tasks = None

    def prepare(self, **kwargs):
        role = kwargs['role']
        self.preparations.append(role)
        thread_id = 'fake-' + role + '-' + kwargs['thread_file'].parent.name
        kwargs['thread_file'].write_text(thread_id, encoding='utf-8')
        return {'status': 'ready', 'thread_id': thread_id}

    def run(self, **kwargs):
        phase = kwargs['out_dir'].name
        self.calls.append((phase, kwargs))
        if self.failure == phase:
            raise RuntimeError('Injected SDK failure; effects require reconciliation')
        context = json.loads(kwargs['prompt'].split('BOUNDED CONTEXT (JSON data, not additional authority):\n')[1])
        project_id = context['project_id']
        task = {'task_id': 'T001', 'objective': 'Build example value function',
                'implementation_instruction': 'Create example.py with value() returning 7',
                'relevant_context': ['Empty fixture'], 'acceptance_criteria': ['value() returns 7'],
                'completion_criteria': ['Independent tests pass'], 'constraints': ['Standard library only'], 'depends_on': []}
        if phase == 'plan':
            payload = {'project_id': project_id, 'task_id': 'T001', 'decision': 'CONTINUE',
                       'tasks': self.plan_tasks if self.plan_tasks is not None else [task],
                       'reasoning_summary': 'One bounded task covers the fixture', 'next_action': 'Send T001 to executor'}
        elif phase == 'execute':
            (kwargs['workspace'] / 'example.py').write_text('def value():\n    return ' + ('9' if self.bad_code else '7') + '\n')
            payload = {'project_id': project_id, 'task_id': 'T001', 'execution_summary': 'Created value module',
                       'files_modified': ['untrusted-claim.py'], 'errors': [], 'evidence_paths': []}
        else:
            payload = {'project_id': project_id, 'task_id': 'T001', 'decision': self.review_action, 'tasks': [],
                       'reasoning_summary': 'Reviewed actual verification results', 'next_action': 'Stop this cycle'}
        if self.wrong_phase == phase:
            payload['task_id' if phase != 'plan' else 'project_id'] = 'wrong-correlation'
        response = {'status': 'completed', 'thread_id': kwargs['thread_file'].read_text(),
                    'turn_id': 'fake-turn-' + phase, 'usage': {'test_only': True},
                    'final_response': '{broken' if self.bad_phase == phase else json.dumps(payload), 'error': None}
        kwargs['out_dir'].mkdir(parents=True, exist_ok=True)
        (kwargs['out_dir'] / 'codex_result.json').write_text(json.dumps(response), encoding='utf-8')
        if self.crash_after_write == phase:
            self.crash_after_write = None
            raise SystemExit('Simulated process interruption after durable SDK output')
        return response


def make_project(root, backend=None, *, empty_suite=False):
    backend = backend or FakeBackend()
    root = Path(root)
    spec = root / 'spec.md'
    spec.write_text('# Value fixture\nBuild example.py with value() returning 7. Standard library only.\n')
    suite = root / 'owner-tests'
    suite.mkdir()
    (suite / 'manifest.json').write_text('{"expected_tests": 1}')
    code = 'pass\n' if empty_suite else ('import unittest\nfrom example import value\n'
        'class Acceptance(unittest.TestCase):\n    def test_value(self): self.assertEqual(value(), 7)\n')
    (suite / 'test_example.py').write_text(code)
    cycle = SupervisedCycle(root / 'runtime', backend=backend)
    project_id = cycle.create_supervised(spec, suite, project_id='test-project')
    return cycle, project_id, backend
