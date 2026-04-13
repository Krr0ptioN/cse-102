from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.design_system.semantic_tokens import semantic_colors
from app.libs.ui_kit.design_system.variants import normalize_option
from app.libs.ui_kit.components.primitives._base import ctk, use_ctk


BADGE_VARIANTS = ("default", "success", "warning", "danger")


def Badge(  # noqa: N802
    master,
    *,
    text: str,
    variant: str = "default",
    **kwargs,
):
    colors = semantic_colors()
    selected = normalize_option(variant, BADGE_VARIANTS, "default")
    color_map = {
        "default": (colors.panel, colors.text),
        "success": (colors.success, "#ffffff"),
        "warning": (colors.warning, "#ffffff"),
        "danger": (colors.danger, "#ffffff"),
    }
    bg, fg = color_map[selected]
    if use_ctk(master) and ctk is not None:
        return ctk.CTkLabel(
            master,
            text=text,
            fg_color=bg,
            text_color=fg,
            corner_radius=0,
            padx=8,
            pady=4,
            **kwargs,
        )
    return tk.Label(master, text=text, bg=bg, fg=fg, padx=8, pady=4, **kwargs)
