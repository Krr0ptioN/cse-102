from __future__ import annotations

import tkinter as tk

from ...design_system import input_size_tokens
from ...design_system import semantic_colors
from ...design_system import resolve_variant
from ._base import ctk, use_ctk


INPUT_SIZES = tuple(input_size_tokens().keys())


def Input(  # noqa: N802
    master,
    *,
    size: str = "md",
    placeholder: str | None = None,
    **kwargs,
):
    colors = semantic_colors()
    _, size_tokens = resolve_variant(size, input_size_tokens(), default="md")

    if use_ctk(master) and ctk is not None:
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("fg_color", colors.surface)
        kwargs.setdefault("border_color", colors.border)
        kwargs.setdefault("text_color", colors.text)
        kwargs.setdefault("placeholder_text", placeholder or "")
        
        # Filter standard tk keys
        if "bg" in kwargs:
            kwargs.setdefault("fg_color", kwargs.pop("bg"))
        if "fg" in kwargs:
            kwargs.setdefault("text_color", kwargs.pop("fg"))
            
        return ctk.CTkEntry(master, **kwargs)

    kwargs.setdefault("bg", colors.surface)
    kwargs.setdefault("fg", colors.text)
    kwargs.setdefault("highlightbackground", colors.border)
    kwargs.setdefault("highlightthickness", 1)
    kwargs.setdefault("bd", 0)

    widget = tk.Entry(master, **kwargs)
    widget.configure(**size_tokens)
    return widget
