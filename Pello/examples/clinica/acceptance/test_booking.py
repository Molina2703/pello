"""Independent acceptance suite. Must live OUTSIDE the Codex-writable workspace."""
import unittest
from concurrent.futures import ThreadPoolExecutor
from booking import ClinicBooking

SLOT = '2026-11-05T09:00:00-05:00'


class ClinicAcceptance(unittest.TestCase):
    def setUp(self):
        self.app = ClinicBooking()

    def test_AC01_confirmed_booking(self):
        result = self.app.reserve(SLOT, 'person-a', 'req-a', True)
        self.assertEqual(result, {'slot': SLOT, 'customer_id': 'person-a', 'request_id': 'req-a'})

    def test_AC02_must_confirm_first(self):
        with self.assertRaises(ValueError):
            self.app.reserve(SLOT, 'person-a', 'req-a', False)
        self.assertIn(SLOT, self.app.slots([SLOT]))

    def test_AC03_no_double_booking(self):
        self.app.reserve(SLOT, 'person-a', 'req-a', True)
        with self.assertRaises(ValueError):
            self.app.reserve(SLOT, 'person-b', 'req-b', True)

    def test_AC04_idempotent_webhook(self):
        first = self.app.reserve(SLOT, 'person-a', 'req-a', True)
        second = self.app.reserve(SLOT, 'person-a', 'req-a', True)
        self.assertEqual(first, second)
        with self.assertRaises(ValueError):
            self.app.reserve('2026-11-05T10:00:00-05:00', 'person-a', 'req-a', True)

    def test_AC05_cancel_releases_slot(self):
        self.app.reserve(SLOT, 'person-a', 'req-a', True)
        self.assertTrue(self.app.cancel('req-a'))
        self.assertFalse(self.app.cancel('req-a'))
        result = self.app.reserve(SLOT, 'person-b', 'req-b', True)
        self.assertEqual(result['customer_id'], 'person-b')

    def test_AC06_available_slots(self):
        other = '2026-11-05T10:00:00-05:00'
        self.app.reserve(SLOT, 'person-a', 'req-a', True)
        self.assertEqual(self.app.slots([SLOT, other]), [other])
        self.app.cancel('req-a')
        self.assertEqual(self.app.slots([SLOT, other]), [SLOT, other])

    def test_AC07_reject_missing_data(self):
        for field in ('slot', 'customer_id', 'request_id'):
            kwargs = dict(slot=SLOT, customer_id='person-a', request_id='req-a', confirmed=True)
            kwargs[field] = '  '
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.app.reserve(**kwargs)

    def test_AC08_concurrent_single_winner(self):
        def attempt(i):
            try:
                self.app.reserve(SLOT, f'person-{i}', f'req-{i}', True)
                return 'ok'
            except ValueError:
                return 'blocked'
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt, range(16)))
        self.assertEqual(results.count('ok'), 1)
        self.assertEqual(results.count('blocked'), 15)
