from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import semantic_colors
from libs.ui_kit.design_system import Typography
from libs.ui_kit.design_system import normalize_option
from libs.ui_kit import ctk, use_ctk


LABEL_VARIANTS = ("default", "muted", "accent", "danger")


def Label(  # noqa: N802
    master,
    *,
    text: str,
    variant: str = "default",
    weight: str = "normal",
    **kwargs,
):
    colors = semantic_colors()
    selected = normalize_option(variant, LABEL_VARIANTS, "default")
    color_map = {
        "default": colors.text,
        "muted": colors.muted,
        "accent": colors.primary,
        "danger": colors.danger,
    }
    fg = color_map[selected]
    font = (Typography.primary_font_family(), 11, weight)

    if use_ctk(master) and ctk is not None:
        return ctk.CTkLabel(master, text=text, text_color=fg, font=font, **kwargs)

    return tk.Label(master, text=text, fg=fg, bg=colors.bg, font=font, **kwargs)
