import copy
import unittest
from unittest.mock import patch
import pricing
from quotes import quote_items


class QuotesAcceptance(unittest.TestCase):
    def items(self):
        return [{'sku': ' b ', 'quantity': 2, 'unit_cents': 100}, {'sku': 'a', 'quantity': 3, 'unit_cents': 25}]

    def test_totals_and_order(self):
        result = quote_items(self.items())
        self.assertEqual(result['subtotal_cents'], 275); self.assertEqual(result['item_count'], 2)
        self.assertEqual([x['sku'] for x in result['items']], ['B', 'A'])

    def test_consumes_verified_dependency(self):
        with patch('pricing.normalize_item', wraps=pricing.normalize_item) as normalize:
            result = quote_items(self.items())
        self.assertEqual(normalize.call_count, 2)
        self.assertEqual(result['items'], [pricing.normalize_item(x) for x in self.items()])

    def test_list_bounds(self):
        for bad in (None, {}, (), '', [], True, self.items() * 51):
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError): quote_items(bad)
        self.assertEqual(quote_items(self.items() * 50)['item_count'], 100)

    def test_invalid_record_propagates(self):
        for bad in (None, {}, {'sku': 'a', 'quantity': False, 'unit_cents': 1}):
            with self.assertRaises(ValueError): quote_items([self.items()[0], bad])

    def test_exact_output_and_no_mutation(self):
        items = self.items(); previous = copy.deepcopy(items)
        result = quote_items(items)
        self.assertEqual(set(result), {'items', 'subtotal_cents', 'item_count'})
        self.assertEqual(items, previous); self.assertIsNot(result['items'], items)
        self.assertIsNot(result['items'][0], items[0])

    def test_deterministic_duplicate_preservation(self):
        items = [self.items()[0], self.items()[0]]
        first = quote_items(items)
        self.assertEqual(first, quote_items(items)); self.assertEqual(first['item_count'], 2)
        self.assertEqual(first['subtotal_cents'], 400)
