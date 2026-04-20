from __future__ import annotations

import tkinter as tk

from ...design_system import semantic_colors
from ...design_system import Typography
from ...design_system import normalize_option
from ._base import ctk, use_ctk


LABEL_VARIANTS = ("default", "muted", "accent", "danger")


def Label(  # noqa: N802
    master,
    *,
    text: str,
    variant: str = "default",
    weight: str = "normal",
    size: str = "md",
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
    
    size_map = {
        "xs": 8,
        "sm": 9,
        "md": 11,
        "lg": 14,
        "xl": 18,
    }
    font_size = size_map.get(size, 11)
    
    fg = color_map[selected]

    # Set defaults in kwargs if not already provided
    kwargs.setdefault("text", text)
    kwargs.setdefault("text_color" if use_ctk(master) else "fg", fg)
    if "font" not in kwargs:
        kwargs["font"] = (Typography.primary_font_family(), font_size, weight)

    if use_ctk(master) and ctk is not None:
        # Filter standard tk keys and custom keys
        if "bg" in kwargs:
            kwargs.setdefault("fg_color", kwargs.pop("bg"))
            
        return ctk.CTkLabel(master, **kwargs)

    # For tk.Label, we need to ensure 'bg' is set if not provided
    kwargs.setdefault("bg", colors.bg)
    return tk.Label(master, **kwargs)

