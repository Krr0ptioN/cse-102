from __future__ import annotations

import customtkinter as ctk

from app.libs.ui_kit.design_system.typography import Typography
from app.libs.ui_kit.design.tokens import PALETTE


def apply_ctk_theme(root: ctk.CTk | None = None) -> None:
    """Configure CustomTkinter global theme using design tokens.

    This keeps the door open for incremental migration: existing Tk pages can
    coexist while new CTk-based shells/components pick up these defaults.
    """

    Typography.ensure_ctk_font(root)
    family = Typography.primary_font_family()

    # Apply global default font for CTk widgets.
    try:
        ctk.set_default_font(family=family, size=11, weight="normal")
    except Exception:
        pass

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")  # base; we'll override key colors below

    # Map key palette entries into CTk defaults where possible.
    ctk.ThemeManager.theme["CTk"] = ctk.ThemeManager.theme.get("CTk", {})
    theme = ctk.ThemeManager.theme["CTk"]

    theme.setdefault("colors", {})
    colors = theme["colors"]
    colors.update(
        {
            "window_bg_color": PALETTE["bg"],
            "frame_low": PALETTE["surface"],
            "frame_high": PALETTE["surface_alt"],
            "text": PALETTE["text"],
            "text_disabled": PALETTE["muted"],
            "button": PALETTE["accent"],
            "button_hover": PALETTE["accent"],
            "border": PALETTE["border"],
        }
    )

    theme.setdefault("font", {})
    font = theme["font"]
    font.update({"family": family, "size": 11, "weight": "normal"})

    # Set global CTk default fonts so widgets without explicit fonts pick it up.
    default_font = Typography._ctk_default_font()
    ctk.ThemeManager._TextFont = default_font
    ctk.ThemeManager._TextFontMono = default_font
