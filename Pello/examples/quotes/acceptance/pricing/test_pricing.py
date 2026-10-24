import copy
import unittest
from pricing import normalize_item


class PricingAcceptance(unittest.TestCase):
    def record(self, **values):
        return dict(sku=' a-1 ', quantity=2, unit_cents=125, **values)

    def test_normalization_and_total(self):
        self.assertEqual(normalize_item(self.record()), {'sku': 'A-1', 'quantity': 2, 'unit_cents': 125, 'total_cents': 250})

    def test_types_exclude_boolean(self):
        for field in ('quantity', 'unit_cents'):
            for bad in (True, False, None, '2', 2.0, []):
                item = self.record(); item[field] = bad
                with self.subTest(field=field, bad=bad), self.assertRaises(ValueError): normalize_item(item)
        for bad in (None, [], 'x', 1):
            with self.assertRaises(ValueError): normalize_item(bad)

    def test_required_fields_and_sku(self):
        for key in ('sku', 'quantity', 'unit_cents'):
            item = self.record(); del item[key]
            with self.assertRaises(ValueError): normalize_item(item)
        for bad in ('', '  ', None, 1, True):
            item = self.record(); item['sku'] = bad
            with self.assertRaises(ValueError): normalize_item(item)

    def test_bounds(self):
        for field, bad_values in (('quantity', (0, -1, 1001)), ('unit_cents', (-1, 100000001))):
            for bad in bad_values:
                item = self.record(); item[field] = bad
                with self.assertRaises(ValueError): normalize_item(item)
        self.assertEqual(normalize_item({'sku': 'z', 'quantity': 1000, 'unit_cents': 100000000})['total_cents'], 100000000000)
        self.assertEqual(normalize_item({'sku': 'z', 'quantity': 1, 'unit_cents': 0})['total_cents'], 0)

    def test_idempotent_and_deterministic(self):
        first = normalize_item(self.record())
        self.assertEqual(normalize_item(first), first)
        self.assertEqual(normalize_item(self.record()), first)

    def test_no_mutation_and_ignored_extras(self):
        source = self.record(extra={'nested': []}); old = copy.deepcopy(source)
        result = normalize_item(source)
        self.assertEqual(source, old); self.assertIsNot(result, source)
        self.assertEqual(set(result), {'sku', 'quantity', 'unit_cents', 'total_cents'})
