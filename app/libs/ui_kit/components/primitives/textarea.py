from __future__ import annotations

import tkinter as tk

from ...design_system import semantic_colors
from ._base import ctk, use_ctk


def TextArea(  # noqa: N802
    master,
    *,
    height: int = 120,
    **kwargs,
):
    colors = semantic_colors()
    if use_ctk(master) and ctk is not None:
        kwargs.setdefault("fg_color", colors.surface)
        kwargs.setdefault("border_color", colors.border)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("text_color", colors.text)
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("height", height)
        return ctk.CTkTextbox(master, **kwargs)

    kwargs.setdefault("bg", colors.surface)
    kwargs.setdefault("fg", colors.text)
    kwargs.setdefault("highlightbackground", colors.border)
    kwargs.setdefault("highlightthickness", 1)
    kwargs.setdefault("bd", 0)
    kwargs.setdefault("height", max(3, int(height / 24)))
    
    return tk.Text(master, **kwargs)
