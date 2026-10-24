"""Trusted independent unittest runner, launched with Python -I."""
import argparse
import json
from pathlib import Path
import sys
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--suite', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.workspace.resolve()))
    suite = unittest.TestLoader().discover(str(args.suite.resolve()), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2, resultclass=CountedResult).run(suite)
    failed_ids = result.failed_ids & result.started_ids
    failed = len(failed_ids)
    skipped = len((result.skipped_ids & result.started_ids) - failed_ids)
    data = {'tests_executed': result.testsRun, 'passed': result.testsRun - failed - skipped,
            'failed': failed, 'skipped': skipped,
            'successful': result.wasSuccessful() and not skipped and result.testsRun > 0}
    args.result.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return 0 if data['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
