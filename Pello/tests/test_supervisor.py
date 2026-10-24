"""Supervisor regression tests (Python standard library)."""
import json
from pathlib import Path
import tempfile
import unittest
from athis_autopilot.supervisor import Supervisor, files_hash

BASE = Path(__file__).resolve().parents[1]


class SupervisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.supervisor = Supervisor(Path(self.tmp.name))

    def new_job(self):
        return self.supervisor.create(BASE / 'examples/clinica/spec.json',
                                      BASE / 'examples/clinica/acceptance', 'mock')

    def test_red_green_and_evidence(self):
        job_id = self.new_job()
        result = self.supervisor.run(job_id)
        self.assertEqual(result['state'], 'LISTO_PARA_REVISION')
        self.assertEqual(result['turns'], 2)
        self.assertEqual(result['fixes'], 1)
        self.assertEqual(result['last_tests'], 8)
        folder = Path(self.tmp.name) / 'jobs' / job_id
        first = (folder / 'evidence' / 'cycle_01_tests.log').read_text()
        second = (folder / 'evidence' / 'cycle_02_tests.log').read_text()
        self.assertIn('FAILED', first)
        self.assertIn('OK', second)
        data = json.loads((folder / 'report.json').read_text())
        self.assertTrue(data['suite_sha256_still_matches'])
        self.assertFalse(data['codex_executed'])

    def test_resume_terminal_is_safe(self):
        job_id = self.new_job()
        first = self.supervisor.run(job_id)
        second = self.supervisor.run(job_id)
        self.assertEqual(first['turns'], second['turns'])

    def test_suite_tamper_fails_closed(self):
        job_id = self.new_job()
        folder = Path(self.tmp.name) / 'jobs' / job_id
        test_file = folder / 'acceptance' / 'test_booking.py'
        test_file.chmod(0o644)
        test_file.write_text('pass\n')
        self.assertNotEqual(files_hash(folder / 'acceptance'), self.supervisor.job(job_id)['suite_hash'])
        result = self.supervisor.run(job_id)
        self.assertEqual(result['state'], 'REQUIERE_REVISION_TECNICA')
        self.assertIn('integrity FAILURE', result['last_error'])

    def test_invalid_spec_rejected(self):
        invalid = Path(self.tmp.name) / 'bad.json'
        invalid.write_text('{"id":"abc"}')
        with self.assertRaises(ValueError):
            self.supervisor.create(invalid, BASE / 'examples/clinica/acceptance', 'mock')


if __name__ == '__main__':
    unittest.main()
