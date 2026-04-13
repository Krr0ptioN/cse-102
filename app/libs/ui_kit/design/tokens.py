from __future__ import annotations

# Design tokens for the upcoming CustomTkinter UI overhaul.
# Keep values ASCII-only to avoid font issues on some platforms.
from app.libs.ui_kit.design_system.typography import Typography

PALETTE = {
    "bg": "#f4f6f8",
    "surface": "#ffffff",
    "surface_alt": "#f0f2f5",
    "border": "#d7dce1",
    "text": "#1f2933",
    "muted": "#5f6b7a",
    "accent": "#2563eb",
    "accent_soft": "#e8efff",
    "success": "#16a34a",
    "warning": "#f59e0b",
    "danger": "#dc2626",
}

SPACING = {
    "xxs": 4,
    "xs": 8,
    "sm": 12,
    "md": 16,
    "lg": 20,
    "xl": 24,
}

SHADOW = {
    "card": (2, 2, 6, 0.12),  # (x, y, blur, alpha)
}

def typography() -> dict[str, tuple[str, int, str]]:
    family = Typography.primary_font_family()
    return {
        "heading": (family, 18, "bold"),
        "title": (family, 14, "bold"),
        "body": (family, 11, "normal"),
        "caption": (family, 10, "normal"),
    }


def palette() -> dict[str, str]:
    return dict(PALETTE)


def spacing(key: str) -> int:
    return SPACING[key]
