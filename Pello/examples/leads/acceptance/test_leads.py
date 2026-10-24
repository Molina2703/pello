"""Owner-authored independent acceptance tests; never given writable to executor."""
import copy
import unittest
from leads import normalize_lead


class LeadAcceptance(unittest.TestCase):
    def record(self, **updates):
        data = {'name': '  Ana   María\tPérez ', 'email': ' ANA.PEREZ+DEV@EXAMPLE.TEST ',
                'phone': ' +57 (300) 123-4567 ', 'source': ' WEB '}
        data.update(updates)
        return data

    def test_01_normalization(self):
        self.assertEqual(normalize_lead(self.record()), {
            'name': 'Ana María Pérez', 'email': 'ana.perez+dev@example.test',
            'phone': '+573001234567', 'source': 'web'})

    def test_02_input_shape(self):
        for value in (None, [], 'record', 1, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_lead(value)

    def test_03_required_fields(self):
        for key in self.record():
            data = self.record(); del data[key]
            with self.subTest(key=key), self.assertRaises(ValueError):
                normalize_lead(data)

    def test_04_required_types(self):
        for key in self.record():
            for value in (None, 123, True, []):
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    normalize_lead(self.record(**{key: value}))

    def test_05_empty_name(self):
        for value in ('', ' \n\t '):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_lead(self.record(name=value))

    def test_06_invalid_email(self):
        for value in ('', 'a@b', 'a@@b.test', 'a b@c.test', '@x.test', 'a@b.c', 'á@x.test', 'a@x.test\nBAD'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                normalize_lead(self.record(email=value))

    def test_07_valid_email(self):
        self.assertEqual(normalize_lead(self.record(email=' A_B.%+1@SUB.EXAMPLE.TEST '))['email'], 'a_b.%+1@sub.example.test')

    def test_08_phone_bounds(self):
        for value in ('1234567', '123456789012345', '+1234567'):
            with self.subTest(value=value): self.assertEqual(normalize_lead(self.record(phone=value))['phone'], value)
        for value in ('123456', '1234567890123456', ''):
            with self.subTest(value=value), self.assertRaises(ValueError): normalize_lead(self.record(phone=value))

    def test_09_phone_characters(self):
        for value in ('++1234567', '12+34567', '123.4567', '123/4567', '123a4567', '１２３４５６７', '123\t4567'):
            with self.subTest(value=value), self.assertRaises(ValueError): normalize_lead(self.record(phone=value))

    def test_10_sources(self):
        for value in (' WEB ', 'Referral', 'EVENT'):
            with self.subTest(value=value): self.assertEqual(normalize_lead(self.record(source=value))['source'], value.strip().lower())
        for value in ('', 'social', 'web event'):
            with self.subTest(value=value), self.assertRaises(ValueError): normalize_lead(self.record(source=value))

    def test_11_new_dictionary(self):
        data = self.record(extra='ignored'); original = copy.deepcopy(data)
        result = normalize_lead(data)
        self.assertEqual(data, original)
        self.assertIsNot(result, data)
        self.assertEqual(set(result), {'name', 'email', 'phone', 'source'})

    def test_12_idempotence(self):
        first = normalize_lead(self.record())
        self.assertEqual(normalize_lead(first), first)
        self.assertEqual(normalize_lead(self.record()), first)
