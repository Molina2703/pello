"""Injected responses and tiny independent suites; never real SDK evidence."""
import json
from pathlib import Path
from uuid import uuid4
from athis_autopilot.pipeline import IncrementalPipeline
from athis_autopilot.pipeline_contracts import PipelinePolicy


class PipelineBackend:
    def __init__(self):
        self.calls = []
        self.fail_first = False
        self.always_bad = False
        self.reject_first_review = False
        self.crash_after_output = False
        self.mutate_review = False
        self.bad_plan = False
        self.block = False
        self.choices = []

    def capabilities(self):
        return {'authenticated': True, 'models': {'gpt-6-luna': ['low', 'medium'], 'gpt-6.1-sol': ['low', 'medium', 'high']},
                'remaining_percent': 60, 'at': 'injected'}

    def prepare(self, **kwargs):
        thread = 'mock-' + kwargs['role'] + '-' + kwargs['thread_file'].parent.name
        kwargs['thread_file'].write_text(thread)
        return {'status': 'ready', 'thread_id': thread}

    def run(self, **kwargs):
        data = json.loads(kwargs['prompt'].split('PIPELINE CONTEXT (JSON):\n')[1])
        phase = kwargs['out_dir'].name
        task = data['current_increment']
        task_id = task['owner']['task_id'] if task else '_plan'
        number = data['attempt']['attempt'] if data['attempt'] else 0
        self.calls.append((task_id, number, phase))
        self.choices.append((kwargs['model'], kwargs['effort']))
        if self.block:
            from athis_autopilot.engines import CodexBlocked
            raise CodexBlocked('Injected quota blocker')
        if phase == 'plan':
            tasks = [{'task_id': t['task_id'], 'objective': t['specification'], 'implementation_instruction': t['specification']}
                     for t in data['owner_contract']['increments']]
            if self.bad_plan: tasks = tasks[:1]
            payload = {'project_id': data['project_id'], 'architecture': ['Two small modules with explicit imports'],
                       'tasks': tasks, 'reasoning_summary': 'Both owner increments planned'}
        elif phase == 'execute':
            if task_id == 'A':
                value = 9 if self.always_bad or (self.fail_first and number == 1) else 7
                (kwargs['workspace'] / 'a.py').write_text(f'def value():\n    return {value}\n')
            else:
                (kwargs['workspace'] / 'b.py').write_text('import a\ndef double():\n    return 2 * a.value()\n')
            payload = {'project_id': data['project_id'], 'task_id': task_id, 'execution_summary': 'Implemented fixture increment',
                       'files_modified': ['untrusted.py'], 'errors': [], 'evidence_paths': []}
        else:
            if self.mutate_review:
                (kwargs['workspace'] / 'a.py').write_text('def value():\n    return 99\n')
            payload = {'project_id': data['project_id'], 'task_id': task_id, 'attempt': number,
                       'verdict': 'FAIL' if self.reject_first_review and number == 1 and task_id == 'A' else 'PASS',
                       'diagnosis': 'implementation' if self.reject_first_review and number == 1 and task_id == 'A' else 'none',
                       'feedback': 'Injected independent review'}
        raw = {'status': 'completed', 'thread_id': kwargs['thread_file'].read_text(), 'turn_id': 'mock-turn-' + uuid4().hex,
               'final_response': json.dumps(payload), 'usage': None}
        kwargs['out_dir'].mkdir(parents=True, exist_ok=True)
        (kwargs['out_dir'] / 'codex_result.json').write_text(json.dumps(raw))
        if self.crash_after_output and phase == 'execute':
            self.crash_after_output = False
            raise SystemExit('Injected process interruption after durable output')
        return raw


def fixture(tmp, backend=None, policy=None):
    root = Path(tmp); backend = backend or PipelineBackend()
    suite = root / 'suites'
    for name in ('a', 'b'): (suite / name).mkdir(parents=True)
    (suite / 'a/test_a.py').write_text('import unittest\nfrom a import value\nclass Check(unittest.TestCase):\n    def test_value(self): self.assertEqual(value(), 7)\n')
    (suite / 'b/test_b.py').write_text('import unittest\nfrom b import double\nclass Check(unittest.TestCase):\n    def test_double(self): self.assertEqual(double(), 14)\n')
    spec = root / 'spec.md'; spec.write_text('# Fixture\nA produces 7, B imports A and doubles it.')
    increments = []
    for task_id, file_name, dependencies in (('A', 'a', []), ('B', 'b', ['A'])):
        increments.append({'task_id': task_id, 'specification': 'Build ' + file_name + '.py from the specification',
            'inputs': ['fictional data'], 'outputs': [file_name + '.py'], 'components': [file_name + '.py'],
            'acceptance_criteria': ['Independent suite passes'], 'depends_on': dependencies,
            'suite': file_name, 'expected_tests': 1, 'risk': 'routine'})
    manifest = root / 'increments.json'
    manifest.write_text(json.dumps({'architecture_constraints': ['Standard library only'], 'tools': [], 'increments': increments}))
    core = IncrementalPipeline(root / 'runtime', backend=backend)
    project_id = core.create_pipeline(spec, suite, manifest, project_id='pipeline-test', policy=policy or PipelinePolicy())
    return core, project_id, backend
