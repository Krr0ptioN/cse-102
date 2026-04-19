from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import semantic_colors
from libs.ui_kit import ctk, use_ctk


def TextArea(  # noqa: N802
    master,
    *,
    height: int = 120,
    **kwargs,
):
    colors = semantic_colors()
    if use_ctk(master) and ctk is not None:
        return ctk.CTkTextbox(
            master,
            fg_color=colors.surface,
            border_color=colors.border,
            border_width=1,
            text_color=colors.text,
            corner_radius=0,
            height=height,
            **kwargs,
        )

    return tk.Text(
        master,
        bg=colors.surface,
        fg=colors.text,
        highlightbackground=colors.border,
        highlightthickness=1,
        bd=0,
        height=max(3, int(height / 24)),
        **kwargs,
    )
