"""Collect the completed Phase 3A run without model calls or operational DB writes."""
from collections import Counter
from contextlib import closing
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3

project = Path(__file__).resolve().parents[2]
evidence = project / 'evidence/phase3a'
runtime = project / 'runtime/supervised/phase3a-quotes-first'
report = json.loads((runtime / 'pipeline-report.json').read_text(encoding='utf-8'))
baseline = json.loads((evidence / 'baseline-tables.json').read_text(encoding='utf-8'))

with closing(sqlite3.connect(project / 'runtime/jobs.sqlite3')) as cx:
    checks = {}
    for name, rows in baseline.items():
        before = Counter(json.dumps(r, sort_keys=True) for r in rows)
        after = Counter(json.dumps(list(r), sort_keys=True) for r in cx.execute('SELECT * FROM ' + name))
        checks[name] = all(after[r] >= n for r, n in before.items())
    integrity = cx.execute('PRAGMA integrity_check').fetchone()[0]

log = (evidence / 'final-all-tests.log').read_text(encoding='utf-8-sig')
test_count = int(re.findall(r'Ran (\d+) tests', log)[-1])
assert log.rstrip().endswith('OK')
assert report['passed'] and report['verified_increments'] == 2
assert len(report['operations']) == 5 and all(o['status'] == 'COMPLETED' for o in report['operations'])
assert all(checks.values()) and integrity == 'ok'
assert [a['attempt'] for a in report['attempts']] == [1, 1]
assert all(c['stage'] == 'COMMITTED' for c in report['checkpoints'])
assert report['checkpoints'][1]['parent_head'] == report['checkpoints'][0]['commit_sha']
first_snapshot = json.loads(report['checkpoints'][0]['snapshot'])
last_snapshot = json.loads(report['checkpoints'][1]['snapshot'])
assert first_snapshot['pricing.py'] == last_snapshot['pricing.py']
original_zip = Path('C:/Users/USUARIO/Downloads/ATHIS-DEV-AUTOPILOT-V1.zip')
expected_archive = '7607e3afc6e011142bc18ffc79ae5ad7aafc6ebb7fc305f5890b75a2169da86e'
archive_unchanged = hashlib.sha256(original_zip.read_bytes()).hexdigest() == expected_archive
assert archive_unchanged

curated = evidence / 'verified-live-pipeline'
curated.mkdir(exist_ok=True)

def preserve_copy(source, destination):
    source = Path(source); destination = Path(destination)
    if destination.exists():
        if source.read_bytes() != destination.read_bytes():
            raise ValueError('Preserved evidence differs; choose a new snapshot directory: ' + str(destination))
        return str(destination)
    return shutil.copy2(source, destination)

for name in ('evidence', 'acceptance'):
    shutil.copytree(runtime / name, curated / name, dirs_exist_ok=True,
                    copy_function=preserve_copy, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
for name in ('pipeline-report.json', 'pipeline-report.md', 'SPEC.md', 'increments.json', 'supervisor-thread.txt', 'executor-thread.txt'):
    preserve_copy(runtime / name, curated / name)
for name in ('pricing.py', 'quotes.py'):
    preserve_copy(runtime / 'workspace' / name, curated / name)
manifest = {p.relative_to(curated).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(curated.rglob('*')) if p.is_file() and p.name != 'manifest-sha256.json'}
(curated / 'manifest-sha256.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

summary = {'status': 'VERIFIED THROUGH REAL CODEX SDK', 'project_id': report['project_id'],
    'implementation_checkpoint': '30ed940', 'phase2_base': '61f52e7',
    'automated_tests_passed': test_count, 'previous_tests_preserved_and_passing': 43,
    'new_tests': test_count - 43, 'verified_increments': 2, 'attempts_per_increment': [1, 1],
    'sdk_turns': [{'phase': o['phase'], 'selection': json.loads(o['request'])['selection'],
                   'thread_id': json.loads(o['response'])['thread_id'], 'turn_id': json.loads(o['response'])['turn_id']}
                  for o in report['operations']],
    'acceptance_unique_tests': 12, 'acceptance_test_executions_including_regression': 18,
    'verification': [e['payload'] for e in report['exchanges'] if e['kind'] == 'verification'],
    'reviews': [e['payload'] for e in report['exchanges'] if e['kind'] == 'review'],
    'checkpoints': report['checkpoints'], 'sessions': report['sessions'],
    'completed_project_reopen_added_operations': 0,
    'usage_latest_total_per_thread': report['usage_latest_total_per_thread'],
    'usage_note': 'Counters cumulative per thread. Latest total once per role; not a verified USD bill.',
    'baseline_rows_preserved': checks, 'sqlite_integrity': integrity,
    'original_archive_unchanged': archive_unchanged, 'source_integrity': report['integrity'],
    'external_integration': 'NOT IMPLEMENTED / NOT VERIFIED', 'full_v1_complete': False,
    'next_milestone': 'Authorized n8n DEV adapter with external-operation journal and reconciliation'}
(project / 'reports/phase3a-result.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'tests': test_count, 'turns': len(report['operations']), 'baseline_rows_preserved': checks,
                  'sqlite_integrity': integrity, 'original_archive_unchanged': archive_unchanged,
                  'curated_files': len(manifest), 'report': 'reports/phase3a-result.json'}, indent=2))
