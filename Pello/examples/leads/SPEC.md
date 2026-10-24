# Deterministic fictional lead normalization

Build `leads.py` with `normalize_lead(record)` using Python's standard library.
It accepts one dictionary and returns a NEW dictionary with exactly the string
keys `name`, `email`, `phone`, and `source`. Ignore additional input keys. Never
modify the input dictionary. Invalid input raises `ValueError`, not another type.

## Acceptance criteria

1. The input must be a dictionary. All four required fields must exist and be
   strings; missing values, `None`, numbers, lists, and booleans are invalid.
2. Normalize name by removing leading/trailing whitespace and collapsing all
   internal whitespace runs to one ASCII space. The normalized name must be
   nonempty. Preserve letter case and Unicode accents.
3. Normalize email by stripping leading/trailing whitespace and lowercasing it.
   Its entire value must match `[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}` using
   ASCII character classes as written. Embedded whitespace is invalid.
4. Strip leading/trailing whitespace from phone. Allow only ASCII digits, spaces,
   hyphens, parentheses, and at most one plus sign at the very start. Remove
   spaces, hyphens and parentheses; preserve a leading plus sign. The normalized
   phone must contain 7 through 15 ASCII digits. Reject all other characters,
   misplaced/multiple plus signs, and non-ASCII numeric characters.
5. Normalize source by stripping and lowercasing it. It must be one of `web`,
   `referral`, or `event`.
6. Return deterministic results, including when an already normalized record is
   normalized again. Do not keep mutable global state.

## Constraints and completion

Use only fictional data. No external APIs, databases, networking, packages,
production systems, or additional agents. Implement the module in the current
workspace. Independent tests live outside it and must not be changed. Completion
requires the independent suite to pass. This entire small module should fit in
one executor turn.
