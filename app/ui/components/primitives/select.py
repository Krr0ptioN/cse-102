from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.design_system.semantic_tokens import semantic_colors
from app.ui.components.primitives._base import ctk, tk_style, use_ctk


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
        return ctk.CTkOptionMenu(
            master,
            values=options,
            variable=variable,
            fg_color=colors.surface,
            button_color=colors.panel,
            button_hover_color=colors.panel,
            text_color=colors.text,
            dropdown_fg_color=colors.surface,
            dropdown_text_color=colors.text,
            corner_radius=0,
            **kwargs,
        )

    tk_style(master)
    combobox = ttk.Combobox(
        master,
        values=options,
        textvariable=variable,
        style="Ds.TCombobox",
        state="readonly",
        **kwargs,
    )
    if options:
        combobox.current(0)
    return combobox
