import pricing


def quote_items(items):
    """Validate and total a nonempty collection of quote line items."""
    if not isinstance(items, list) or not 1 <= len(items) <= 100:
        raise ValueError("items must be a nonempty list of at most 100 records")

    normalized = [pricing.normalize_item(record) for record in items]
    return {
        "items": normalized,
        "subtotal_cents": sum(item["total_cents"] for item in normalized),
        "item_count": len(normalized),
    }