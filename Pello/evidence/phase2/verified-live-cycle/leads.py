"""Deterministic normalization for fictional lead records."""

import re


_EMAIL_PATTERN = re.compile(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", re.ASCII)
_PHONE_CHARACTERS = frozenset("0123456789 -()")
_ALLOWED_SOURCES = frozenset(("web", "referral", "event"))
_REQUIRED_FIELDS = ("name", "email", "phone", "source")


def normalize_lead(record):
    """Validate and normalize one lead, returning a fresh dictionary.

    Invalid records raise ``ValueError``. Additional input keys are ignored.
    """
    if not isinstance(record, dict):
        raise ValueError("record must be a dictionary")

    if any(field not in record or not isinstance(record[field], str) for field in _REQUIRED_FIELDS):
        raise ValueError("record must contain all required fields as strings")

    name = " ".join(record["name"].split())
    if not name:
        raise ValueError("name must not be empty")

    email = record["email"].strip().lower()
    if _EMAIL_PATTERN.fullmatch(email) is None:
        raise ValueError("email is invalid")

    phone = record["phone"].strip()
    plus = phone.startswith("+")
    digits = []
    for index, character in enumerate(phone):
        if character == "+":
            if index != 0 or not plus:
                raise ValueError("phone plus sign is misplaced")
        elif character in _PHONE_CHARACTERS:
            if character.isascii() and character.isdigit():
                digits.append(character)
        else:
            raise ValueError("phone contains an invalid character")

    if not 7 <= len(digits) <= 15:
        raise ValueError("phone must contain 7 through 15 ASCII digits")
    normalized_phone = ("+" if plus else "") + "".join(digits)

    source = record["source"].strip().lower()
    if source not in _ALLOWED_SOURCES:
        raise ValueError("source is invalid")

    return {"name": name, "email": email, "phone": normalized_phone, "source": source}
