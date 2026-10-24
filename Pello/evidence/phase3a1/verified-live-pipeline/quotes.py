"""Build fictional quotes from normalized line items."""

import pricing


def quote_items(items):
    """Normalize quote items and calculate the quote subtotal."""
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError("items must be a list containing 1 to 100 records")

    normalized_items = []
    subtotal_cents = 0
    for record in items:
        normalized = pricing.normalize_item(record)
        normalized_items.append(normalized)
        subtotal_cents += normalized["total_cents"]

    return {
        "items": normalized_items,
        "subtotal_cents": subtotal_cents,
        "item_count": len(normalized_items),
    }
