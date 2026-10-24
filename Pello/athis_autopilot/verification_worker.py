"""Trusted independent unittest runner, launched with Python -I."""
import argparse
import json
from pathlib import Path
import sys
import unittest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--suite', type=Path, required=True)
    parser.add_argument('--result', type=Path, required=True)
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(args.workspace.resolve()))
    suite = unittest.TestLoader().discover(str(args.suite.resolve()), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    failed = len(result.failures) + len(result.errors) + len(result.unexpectedSuccesses)
    skipped = len(result.skipped) + len(result.expectedFailures)
    data = {'tests_executed': result.testsRun, 'passed': result.testsRun - failed - skipped,
            'failed': failed, 'skipped': skipped,
            'successful': result.wasSuccessful() and not skipped and result.testsRun > 0}
    args.result.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return 0 if data['successful'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
