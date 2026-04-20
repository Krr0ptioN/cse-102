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
    is_ctk = use_ctk(master) and ctk is not None
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

    # CustomTkinter uses 'text_color', Tkinter uses 'fg'
    if is_ctk:
        kwargs.setdefault("text_color", fg)
    else:
        kwargs.setdefault("fg", fg)

    if "font" not in kwargs:
        family = Typography.primary_font_family()
        if is_ctk and ctk is not None:
            try:
                kwargs["font"] = ctk.CTkFont(
                    family=family,
                    size=font_size,
                    weight=weight,
                )
            except Exception:
                kwargs["font"] = (family, font_size, weight)
        else:
            kwargs["font"] = (family, font_size, weight)

    if is_ctk and ctk is not None:
        # Filter standard tk keys and custom keys
        if "bg" in kwargs:
            kwargs.setdefault("fg_color", kwargs.pop("bg"))

        # Ensure we don't pass 'fg' to CTk
        if "fg" in kwargs:
            kwargs.setdefault("text_color", kwargs.pop("fg"))

        return ctk.CTkLabel(master, **kwargs)
    # For tk.Label, we need to ensure 'bg' is set if not provided
    kwargs.setdefault("bg", colors.bg)
    return tk.Label(master, **kwargs)
