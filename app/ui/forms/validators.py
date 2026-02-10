from __future__ import annotations

import re


def required(value: str) -> str | None:
    if not value.strip():
        return "This field is required."
    return None


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def email(value: str) -> str | None:
    if value and not EMAIL_RE.match(value.strip()):
        return "Enter a valid email address."
    return None


def is_int(value: str) -> str | None:
    if value and not value.strip().isdigit():
        return "Enter a whole number."
    return None


def max_len(limit: int):
    def _check(value: str) -> str | None:
        if value and len(value.strip()) > limit:
            return f"Must be {limit} characters or fewer."
        return None

    return _check
