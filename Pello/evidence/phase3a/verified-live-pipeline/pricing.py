def normalize_item(record):
    """Return a validated, normalized copy of a quote line item."""
    if not isinstance(record, dict):
        raise ValueError("record must be a dict")

    sku = record.get("sku")
    quantity = record.get("quantity")
    unit_cents = record.get("unit_cents")

    if not isinstance(sku, str) or not sku.strip():
        raise ValueError("sku must be a nonempty string")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= 1000:
        raise ValueError("quantity must be an integer from 1 to 1000")
    if isinstance(unit_cents, bool) or not isinstance(unit_cents, int) or not 0 <= unit_cents <= 100000000:
        raise ValueError("unit_cents must be an integer from 0 to 100000000")

    return {
        "sku": sku.strip().upper(),
        "quantity": quantity,
        "unit_cents": unit_cents,
        "total_cents": quantity * unit_cents,
    }