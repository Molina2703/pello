"""Validation and normalization for fictional quote items."""


def normalize_item(record):
    """Return a normalized copy of a quote item.

    ``record`` must provide a non-empty SKU, a quantity from 1 to 1000,
    and a unit price in cents from 0 to 100,000,000.
    """
    if not isinstance(record, dict):
        raise ValueError("record must be a dict")

    try:
        sku = record["sku"]
        quantity = record["quantity"]
        unit_cents = record["unit_cents"]
    except KeyError as exc:
        raise ValueError("record is missing a required field") from exc

    if not isinstance(sku, str) or not sku.strip():
        raise ValueError("sku must be a non-empty string")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or not 1 <= quantity <= 1000:
        raise ValueError("quantity must be an integer from 1 to 1000")
    if isinstance(unit_cents, bool) or not isinstance(unit_cents, int) or not 0 <= unit_cents <= 100_000_000:
        raise ValueError("unit_cents must be an integer from 0 to 100000000")

    return {
        "sku": sku.strip().upper(),
        "quantity": quantity,
        "unit_cents": unit_cents,
        "total_cents": quantity * unit_cents,
    }
