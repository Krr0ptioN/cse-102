from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CoreColorTokens:
    slate_50: str = "#f8fafc"
    slate_100: str = "#f1f5f9"
    slate_200: str = "#e2e8f0"
    slate_500: str = "#64748b"
    slate_900: str = "#0f172a"

    blue_600: str = "#2563eb"
    blue_700: str = "#1d4ed8"
    blue_100: str = "#dbeafe"

    green_600: str = "#16a34a"
    amber_500: str = "#f59e0b"
    red_600: str = "#dc2626"


@dataclass(frozen=True)
class CoreSpacingTokens:
    xxs: int = 4
    xs: int = 8
    sm: int = 12
    md: int = 16
    lg: int = 20
    xl: int = 24


@dataclass(frozen=True)
class CoreRadiusTokens:
    none: int = 0
    sm: int = 4
    md: int = 8


def core_colors() -> CoreColorTokens:
    return CoreColorTokens()


def core_spacing() -> CoreSpacingTokens:
    return CoreSpacingTokens()


def core_radius() -> CoreRadiusTokens:
    return CoreRadiusTokens()
