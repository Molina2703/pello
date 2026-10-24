"""Preserve this phase's new local SDK fixture; never mutate historical runtime."""
from pathlib import Path
import hashlib
import json
import shutil

project = Path(__file__).resolve().parents[2]
evidence = Path(__file__).resolve().parent
runtime = project / 'runtime/phase3a1/supervised/phase3a1-quotes-first'
report = json.loads((runtime / 'pipeline-report.json').read_text(encoding='utf-8'))
assert report['passed'] and report['stage'] == 'COMPLETE', report['blocker']
assert len(report['operations']) == 5 and len(report['checkpoints']) == 2
assert all(op['status'] == 'COMPLETED' for op in report['operations'])
sessions = {s['role']: s['thread_id'] for s in report['sessions']}
assert set(sessions) == {'planner', 'executor', 'reviewer'} and len(set(sessions.values())) == 3
contexts = []
submissions = []
turns = []
for op in report['operations']:
    request, response = json.loads(op['request']), json.loads(op['response'])
    assert response['status'] == 'completed' and response['thread_id'] == sessions[request['role']]
    submission = json.loads((runtime / 'evidence' / op['phase'] / 'model-turn-submitted.json').read_text())
    assert (submission['model'], submission['effort']) == (request['selection']['model'], request['selection']['effort'])
    submissions.append(submission)
    turns.append({'phase': op['phase'], 'role': request['role'], 'selection': request['selection'],
                  'thread_id': response['thread_id'], 'turn_id': response['turn_id'], 'sandbox': submission['sandbox']})
    if request['role'] == 'reviewer':
        context = json.loads(request['prompt'].split('PIPELINE CONTEXT (JSON):\n')[1])
        assert 'global_plan' not in context and 'execution' not in context
        assert set(context['current_increment']) == {'owner'}
        assert context['verification']['passed'] and context['actual_source'] and context['git_diff']
        assert submission['sandbox'] == 'read-only' and submission['approval_mode'] == 'deny_all'
        contexts.append({'phase': op['phase'], 'keys': list(context), 'objective_context_only': True})

baseline = json.loads((evidence / 'preservation-baseline.json').read_text(encoding='utf-8'))
unchanged = {name: hashlib.sha256((project / name).read_bytes()).hexdigest() == digest
             for name, digest in baseline.items()}
assert all(unchanged.values()), [name for name, ok in unchanged.items() if not ok]
curated = evidence / 'verified-live-pipeline'
curated.mkdir(exist_ok=False)
for name in ('evidence', 'acceptance'):
    shutil.copytree(runtime / name, curated / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
for name in ('SPEC.md', 'increments.json', 'pipeline-report.json', 'pipeline-report.md',
             'planner-thread.txt', 'executor-thread.txt', 'reviewer-thread.txt'):
    shutil.copy2(runtime / name, curated / name)
for name in ('pricing.py', 'quotes.py'):
    shutil.copy2(runtime / 'workspace' / name, curated / name)
manifest = {p.relative_to(curated).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(curated.rglob('*')) if p.is_file()}
(curated / 'manifest-sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
source_files = ['ai_supervisor.py', 'bridge.py', 'codex_worker.py', 'model_policy.py',
                'pipeline.py', 'pipeline_contracts.py', 'verification_worker.py']
summary = {'status': 'VERIFIED THROUGH REAL CODEX SDK', 'project_id': report['project_id'],
    'sessions': sessions, 'turns': turns, 'review_contexts': contexts,
    'verification': [e['payload'] for e in report['exchanges'] if e['kind'] == 'verification'],
    'reviews': [e['payload'] for e in report['exchanges'] if e['kind'] == 'review'],
    'checkpoints': report['checkpoints'], 'original_files_unchanged': len(unchanged),
    'usage_latest_total_per_thread': report['usage_latest_total_per_thread'],
    'implementation_sha256': {name: hashlib.sha256((project / 'athis_autopilot' / name).read_bytes()).hexdigest() for name in source_files},
    'external_integration': 'NOT IMPLEMENTED; NO n8n OPERATIONS', 'full_v1_complete': False}
(evidence / 'live-result.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'status': summary['status'], 'sessions': sessions, 'turns': len(turns),
                  'preserved_original_files': len(unchanged), 'curated_files': len(manifest)}, indent=2))
