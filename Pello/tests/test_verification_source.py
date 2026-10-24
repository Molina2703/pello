"""Real verifier regressions; model responses are injected, never live SDK evidence."""
import hashlib
import json
import os
from pathlib import Path
import py_compile
import subprocess
import sys
import tempfile
import unittest

from pipeline_support import PipelineBackend, fixture
from phase2_support import FakeBackend, make_project
from athis_autopilot.pipeline_contracts import PipelinePolicy

BASE = Path(__file__).resolve().parents[1]
WORKER = BASE / 'athis_autopilot/verification_worker.py'


def stale_cache(source, *, cached=7, current=9):
    source.write_text(f'def value():\n    return {cached}\n', encoding='utf-8')
    stamp = source.stat()
    compiled = Path(py_compile.compile(str(source), doraise=True))
    source.write_text(f'def value():\n    return {current}\n', encoding='utf-8')
    os.utime(source, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
    assert source.stat().st_size == stamp.st_size
    assert int(source.stat().st_mtime) == int(stamp.st_mtime)
    return compiled


class CachedPipelineBackend(PipelineBackend):
    def run(self, **kwargs):
        response = super().run(**kwargs)
        if kwargs['out_dir'].name == 'execute' and (kwargs['workspace'] / 'a.py').exists():
            stale_cache(kwargs['workspace'] / 'a.py')
        return response


class SourceVerificationTests(unittest.TestCase):
    def run_worker(self, root, workspace, suite):
        output = root / 'result.json'
        proc = subprocess.run([sys.executable, '-I', str(WORKER), '--workspace', str(workspace),
                               '--suite', str(suite), '--result', str(output)],
                              cwd=workspace, capture_output=True, text=True, timeout=30)
        return proc, json.loads(output.read_text(encoding='utf-8'))

    def value_fixture(self, root):
        workspace = root / 'workspace'; workspace.mkdir()
        suite = root / 'acceptance'; suite.mkdir()
        (suite / 'test_value.py').write_text('import unittest\nfrom example import value\n'
            'class Check(unittest.TestCase):\n    def test_value(self): self.assertEqual(value(), 7)\n')
        return workspace, suite

    def test_stale_bytecode_fails_and_original_files_remain_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); workspace, suite = self.value_fixture(root)
            cache = stale_cache(workspace / 'example.py')
            before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in (cache, workspace / 'example.py')}
            proc, result = self.run_worker(root, workspace, suite)
            self.assertEqual(proc.returncode, 1, proc.stderr)
            self.assertFalse(result['successful']); self.assertEqual(result['failed'], 1)
            self.assertIn('9 != 7', proc.stderr)
            self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in before})

    def test_current_correct_source_passes_despite_wrong_cached_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); workspace, suite = self.value_fixture(root)
            cache = stale_cache(workspace / 'example.py', cached=9, current=7)
            before = cache.read_bytes()
            proc, result = self.run_worker(root, workspace, suite)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(result['successful']); self.assertEqual(result['passed'], 1)
            self.assertEqual(cache.read_bytes(), before)

    def test_sourceless_project_bytecode_cannot_supply_acceptance_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); workspace, suite = self.value_fixture(root)
            source = workspace / 'example.py'; source.write_text('def value(): return 7\n')
            py_compile.compile(str(source), cfile=str(workspace / 'example.pyc'), doraise=True)
            source.unlink()
            proc, result = self.run_worker(root, workspace, suite)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(result['successful'])

    def test_mutation_of_materialized_source_invalidates_verification(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); workspace, suite = self.value_fixture(root)
            source = workspace / 'example.py'
            original = ('from pathlib import Path\nPath(__file__).write_text("def value(): return 9\\n")\n'
                        'def value(): return 7\n')
            source.write_text(original)
            proc, result = self.run_worker(root, workspace, suite)
            self.assertFalse(result['successful'])
            self.assertFalse(result['materialized_integrity'])
            self.assertEqual(source.read_text(), original)

    def test_pipeline_failure_has_no_approval_checkpoint_or_dependent_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, backend = fixture(tmp, backend=CachedPipelineBackend(), policy=PipelinePolicy(max_attempts=1))
            report = core.run_pipeline(pid)
            self.assertFalse(report['passed']); self.assertEqual(report['stage'], 'BLOCKED')
            self.assertEqual(report['checkpoints'], [])
            self.assertEqual([t['state'] for t in report['tasks']], ['FAILED', 'PENDING'])
            self.assertFalse(any(call[0] == 'B' for call in backend.calls))
            self.assertIn('9 != 7', report['attempts'][0]['feedback'])
            self.assertFalse(next(e['payload'] for e in report['exchanges'] if e['kind'] == 'verification')['passed'])

    def test_phase2_also_rejects_stale_bytecode(self):
        class Backend(FakeBackend):
            def run(self, **kwargs):
                response = super().run(**kwargs)
                if kwargs['out_dir'].name == 'execute': stale_cache(kwargs['workspace'] / 'example.py')
                return response
        with tempfile.TemporaryDirectory() as tmp:
            core, pid, _ = make_project(tmp, backend=Backend())
            result = core.run_supervised(pid)
            self.assertFalse(result['passed'])
            self.assertEqual(result['verification']['failed'], 1)

    def test_historical_acceptance_from_preserved_source(self):
        cases = [('phase2/verified-live-cycle', ['leads.py'], [('acceptance', 12)]),
                 ('phase3a/verified-live-pipeline', ['pricing.py', 'quotes.py'],
                  [('acceptance/pricing', 6), ('acceptance/quotes', 6)])]
        import shutil
        for location, modules, suites in cases:
            with self.subTest(location=location), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp); workspace = root / 'workspace'; workspace.mkdir()
                preserved = BASE / 'evidence' / location
                for name in modules: shutil.copy2(preserved / name, workspace / name)
                for index, (suite, expected) in enumerate(suites):
                    run = root / str(index); run.mkdir()
                    proc, result = self.run_worker(run, workspace, preserved / suite)
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    self.assertEqual(result['passed'], expected)
