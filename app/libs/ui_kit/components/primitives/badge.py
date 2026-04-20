from __future__ import annotations

import tkinter as tk

from ...design_system import semantic_colors
from ...design_system import normalize_option
from ._base import ctk, use_ctk


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
        kwargs.setdefault("text", text)
        kwargs.setdefault("fg_color", bg)
        kwargs.setdefault("text_color", fg)
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("padx", 8)
        kwargs.setdefault("pady", 4)
        return ctk.CTkLabel(master, **kwargs)
    
    kwargs.setdefault("bg", bg)
    kwargs.setdefault("fg", fg)
    kwargs.setdefault("padx", 8)
    kwargs.setdefault("pady", 4)
    return tk.Label(master, text=text, **kwargs)
