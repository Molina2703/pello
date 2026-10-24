"""Trusted independent unittest runner, launched with Python -I."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest


class CountedResult(unittest.TextTestResult):
    """Count methods, not individual failing subtests, in the structured report."""
    def __init__(self, *args):
        super().__init__(*args)
        self.started_ids = set(); self.failed_ids = set(); self.skipped_ids = set()
        self.current_id = None

    def startTest(self, test):
        self.current_id = test.id(); self.started_ids.add(test.id())
        super().startTest(test)

    def addError(self, test, err):
        self.failed_ids.add(test.id()); super().addError(test, err)

    def addFailure(self, test, err):
        self.failed_ids.add(test.id()); super().addFailure(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None: self.failed_ids.add(test.id())
        super().addSubTest(test, subtest, err)

    def addUnexpectedSuccess(self, test):
        self.failed_ids.add(test.id()); super().addUnexpectedSuccess(test)

    def addSkip(self, test, reason):
        self.skipped_ids.add(self.current_id or test.id()); super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.skipped_ids.add(test.id()); super().addExpectedFailure(test, err)


def source_copy(source, destination):
    """Materialize source/data only, never importing executor-supplied bytecode."""
    def ignore(directory, names):
        ignored = {n for n in names if n in ('.git', '__pycache__') or n.endswith(('.pyc', '.pyo'))}
        for name in set(names) - ignored:
            path = Path(directory) / name
            if path.is_symlink() or (hasattr(path, 'is_junction') and path.is_junction()):
                raise ValueError('Verification source links are not supported')
        return ignored
    shutil.copytree(source, destination, ignore=ignore)


def snapshot(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--suite', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    workspace, acceptance, output = args.workspace.resolve(), args.suite.resolve(), args.result.resolve()
    original_cwd = Path.cwd()
    # -I excludes cwd/PYTHONPATH. Both project and suite imports now resolve in
    # fresh trees with no .pyc/.pyo, including legacy sourceless bytecode files.
    # Do not delete or chmod anything in the original workspace or acceptance.
    with tempfile.TemporaryDirectory(prefix='pello-verify-') as temporary:
        clean = Path(temporary)
        source_copy(workspace, clean / 'workspace')
        source_copy(acceptance, clean / 'acceptance')
        before = snapshot(clean)
        sys.path.insert(0, str(clean / 'workspace'))
        try:
            os.chdir(clean / 'workspace')
            suite = unittest.TestLoader().discover(str(clean / 'acceptance'), pattern='test_*.py')
            result = unittest.TextTestRunner(verbosity=2, resultclass=CountedResult).run(suite)
            materialized_integrity = snapshot(clean) == before
        finally:
            os.chdir(original_cwd)
            sys.path.remove(str(clean / 'workspace'))
        if not materialized_integrity:
            print('Verification source or acceptance copy changed during tests', file=sys.stderr)
    failed_ids = result.failed_ids & result.started_ids
    failed = len(failed_ids)
    skipped = len((result.skipped_ids & result.started_ids) - failed_ids)
    data = {'tests_executed': result.testsRun, 'passed': result.testsRun - failed - skipped,
            'failed': failed, 'skipped': skipped,
            'materialized_integrity': materialized_integrity,
            'successful': result.wasSuccessful() and not skipped and result.testsRun > 0 and materialized_integrity}
    output.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return 0 if data['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
