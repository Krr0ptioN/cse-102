from __future__ import annotations

from collections.abc import Mapping


def normalize_option(value: str | None, allowed: tuple[str, ...], default: str) -> str:
    if not value:
        return default
    normalized = value.lower().strip()
    if normalized in allowed:
        return normalized
    return default


def resolve_variant[T](
    value: str | None,
    variants: Mapping[str, T],
    *,
    default: str,
) -> tuple[str, T]:
    allowed = tuple(variants.keys())
    selected = normalize_option(value, allowed, default)
    return selected, variants[selected]
