"""One real SDK turn, with independent verification and persistent evidence."""
import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from .engines import run_codex, CodexBlocked
from .installation import check_auth

PROMPT = '''Installation smoke test. Work ONLY in the current workspace.
Create a file named pello_probe.py containing ONLY this unannotated function:
def add(a, b):
    return a + b
Use the file editing tool to create it. Do not run shell commands, access networks,
read credentials, use plugins/MCP, or modify other files. Finish after writing it.
The installer independently checks the file and runs tests outside your workspace.
'''

VERIFIER = '''import importlib.util, pathlib, sys, unittest
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('pello_probe', pathlib.Path(sys.argv[1]))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
class ProbeTests(unittest.TestCase):
    def test_positive(self): self.assertEqual(module.add(2, 3), 5)
    def test_negative(self): self.assertEqual(module.add(-8, 3), -5)
    def test_zero(self): self.assertEqual(module.add(0, 0), 0)
    def test_float(self): self.assertAlmostEqual(module.add(0.1, 0.2), 0.3)
    def test_large(self): self.assertEqual(module.add(10**40, 1), 10**40 + 1)
    def test_unchanged_arguments(self):
        values = [1]; self.assertEqual(module.add(values, [2]), [1, 2]); self.assertEqual(values, [1])
unittest.main(argv=['probe'], verbosity=2)
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--timeout', type=int, default=120)
    args = parser.parse_args()
    project = Path(__file__).resolve().parent.parent
    folder = (args.output or project / 'runtime' / 'sdk-smoke' /
              datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')).resolve()
    if folder.exists():
        parser.error('Output already exists; refusing to repeat a possibly completed turn')
    workspace = folder / 'workspace'
    workspace.mkdir(parents=True)
    result = {'status': 'BLOCKED', 'started_at': datetime.now(timezone.utc).isoformat(),
              'workspace': str(workspace), 'turns_attempted': 0, 'tests_passed': False}
    try:
        result['authentication'] = check_auth()
        if not result['authentication'].get('authenticated'):
            raise CodexBlocked('ChatGPT login unavailable; run pello login')
        subprocess.run(['git', 'init', '-q', str(workspace)], check=True)
        result['turns_attempted'] = 1
        outcome = run_codex(workspace, PROMPT, folder / 'thread_id.txt', folder / 'sdk', args.timeout)
        result['sdk'] = outcome
        source = workspace / 'pello_probe.py'
        text = source.read_text(encoding='utf-8')
        # Check the whole AST before importing any generated code. The only
        # permitted program is the requested function; comments are harmless.
        if ast.dump(ast.parse(text)) != ast.dump(ast.parse('def add(a, b):\n    return a + b\n')):
            raise ValueError('Generated module differs from the safe expected AST; not executed')
        result['source_sha256'] = hashlib.sha256(source.read_bytes()).hexdigest()
        result['changed_files'] = subprocess.check_output(
            ['git', 'ls-files', '--others', '--exclude-standard'], cwd=workspace,
            text=True, encoding='utf-8').splitlines()
        (folder / 'verifier.py').write_text(VERIFIER, encoding='utf-8')
        checked = subprocess.run([sys.executable, '-I', str(folder / 'verifier.py'), str(source)],
                                 capture_output=True, text=True, encoding='utf-8', timeout=30)
        (folder / 'independent-tests.log').write_text(checked.stdout + checked.stderr, encoding='utf-8')
        result['tests_passed'] = checked.returncode == 0
        result['test_count'] = 6
        result['status'] = 'REAL INTEGRATION VERIFIED' if result['tests_passed'] else 'FAILED'
    except CodexBlocked as exc:
        result['reason'] = str(exc)
    except Exception as exc:
        result['status'] = 'FAILED'
        result['reason'] = f'{type(exc).__name__}: {exc}'
    finally:
        result['finished_at'] = datetime.now(timezone.utc).isoformat()
        (folder / 'result.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        print(json.dumps(result, indent=2, ensure_ascii=False))
        print('EVIDENCE:', folder)
    return 0 if result['status'] == 'REAL INTEGRATION VERIFIED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
