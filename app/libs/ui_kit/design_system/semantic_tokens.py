from __future__ import annotations

from dataclasses import dataclass

from .core_tokens import core_colors


@dataclass(frozen=True)
class SemanticColorTokens:
    bg: str
    surface: str
    panel: str
    border: str
    text: str
    muted: str
    primary: str
    primary_hover: str
    primary_soft: str
    success: str
    warning: str
    danger: str


def semantic_colors() -> SemanticColorTokens:
    c = core_colors()
    return SemanticColorTokens(
        bg=c.slate_50,
        surface="#ffffff",
        panel=c.slate_100,
        border=c.slate_200,
        text=c.slate_900,
        muted=c.slate_500,
        primary=c.blue_600,
        primary_hover=c.blue_700,
        primary_soft=c.blue_100,
        success=c.green_600,
        warning=c.amber_500,
        danger=c.red_600,
    )
