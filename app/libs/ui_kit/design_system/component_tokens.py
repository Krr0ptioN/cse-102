from __future__ import annotations

from dataclasses import dataclass

from libs.ui_kit.design_system import core_radius, core_spacing
from libs.ui_kit.design_system import semantic_colors


@dataclass(frozen=True)
class ButtonVariantTokens:
    bg: str
    fg: str
    border: str
    hover: str


def button_variants() -> dict[str, ButtonVariantTokens]:
    colors = semantic_colors()
    return {
        "default": ButtonVariantTokens(
            bg=colors.primary,
            fg="#ffffff",
            border=colors.primary,
            hover=colors.primary_hover,
        ),
        "secondary": ButtonVariantTokens(
            bg=colors.panel,
            fg=colors.text,
            border=colors.border,
            hover=colors.surface,
        ),
        "outline": ButtonVariantTokens(
            bg=colors.surface,
            fg=colors.text,
            border=colors.border,
            hover=colors.panel,
        ),
        "ghost": ButtonVariantTokens(
            bg=colors.bg,
            fg=colors.text,
            border=colors.bg,
            hover=colors.panel,
        ),
        "danger": ButtonVariantTokens(
            bg=colors.danger,
            fg="#ffffff",
            border=colors.danger,
            hover=colors.danger,
        ),
    }


def button_size_tokens() -> dict[str, dict[str, int]]:
    spacing = core_spacing()
    return {
        "sm": {"padx": spacing.sm, "pady": spacing.xs},
        "md": {"padx": spacing.md, "pady": spacing.sm},
        "lg": {"padx": spacing.lg, "pady": spacing.md},
    }


def input_size_tokens() -> dict[str, dict[str, int]]:
    spacing = core_spacing()
    return {
        "sm": {"ipady": spacing.xxs},
        "md": {"ipady": spacing.xs},
        "lg": {"ipady": spacing.sm},
    }


def card_tokens() -> dict[str, str | int]:
    colors = semantic_colors()
    radius = core_radius()
    return {
        "bg": colors.panel,
        "border": colors.border,
        "radius": radius.none,
    }


def card_size_tokens() -> dict[str, dict[str, int]]:
    """Named card dimensions in pixels."""

    return {
        "sm": {"width": 280, "height": 140},
        "md": {"width": 360, "height": 200},
        "lg": {"width": 480, "height": 280},
        "xl": {"width": 640, "height": 360},
    }
