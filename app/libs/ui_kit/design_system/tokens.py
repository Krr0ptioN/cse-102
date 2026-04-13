from __future__ import annotations

from dataclasses import dataclass

from app.libs.ui_kit.design_system.component_tokens import button_variants
from app.libs.ui_kit.design_system.semantic_tokens import semantic_colors


@dataclass(frozen=True)
class Palette:
    bg: str
    surface: str
    panel: str
    border: str
    text: str
    muted: str
    primary: str


def palette() -> Palette:
    colors = semantic_colors()
    return Palette(
        bg=colors.bg,
        surface=colors.surface,
        panel=colors.panel,
        border=colors.border,
        text=colors.text,
        muted=colors.muted,
        primary=colors.primary,
    )


def legacy_palette_dict() -> dict[str, str]:
    """Compatibility helper for dict-based consumers."""

    p = palette()
    return {
        "bg": p.bg,
        "surface": p.surface,
        "panel": p.panel,
        "border": p.border,
        "text": p.text,
        "muted": p.muted,
        "primary": p.primary,
        "accent": p.primary,
        "accent_light": semantic_colors().primary_soft,
    }


def component_variant_catalog() -> dict[str, tuple[str, ...]]:
    """Variant registry for docs/debugging."""

    return {
        "button": tuple(button_variants().keys()),
    }
