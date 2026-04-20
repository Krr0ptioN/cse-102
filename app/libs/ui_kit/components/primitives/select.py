from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ...design_system import semantic_colors
from ._base import ctk, tk_style, use_ctk


def Select(  # noqa: N802
    master,
    *,
    values: list[str] | tuple[str, ...],
    variable: tk.StringVar | None = None,
    **kwargs,
):
    colors = semantic_colors()
    options = list(values)
    variable = variable or tk.StringVar(value=(options[0] if options else ""))

    if use_ctk(master) and ctk is not None:
        kwargs.setdefault("values", options)
        kwargs.setdefault("variable", variable)
        kwargs.setdefault("fg_color", colors.surface)
        kwargs.setdefault("button_color", colors.panel)
        kwargs.setdefault("button_hover_color", colors.panel)
        kwargs.setdefault("text_color", colors.text)
        kwargs.setdefault("dropdown_fg_color", colors.surface)
        kwargs.setdefault("dropdown_text_color", colors.text)
        kwargs.setdefault("corner_radius", 0)
        return ctk.CTkOptionMenu(master, **kwargs)

    tk_style(master)
    kwargs.setdefault("values", options)
    kwargs.setdefault("textvariable", variable)
    kwargs.setdefault("style", "Ds.TCombobox")
    kwargs.setdefault("state", "readonly")
    
    combobox = ttk.Combobox(master, **kwargs)
    if options:
        combobox.current(0)
    return combobox
