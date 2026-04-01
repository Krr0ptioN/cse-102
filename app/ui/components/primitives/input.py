from __future__ import annotations

import tkinter as tk

from app.design_system.component_tokens import input_size_tokens
from app.design_system.semantic_tokens import semantic_colors
from app.design_system.variants import resolve_variant
from app.ui.components.primitives._base import ctk, use_ctk


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
        widget = ctk.CTkEntry(
            master,
            corner_radius=0,
            fg_color=colors.surface,
            border_color=colors.border,
            text_color=colors.text,
            placeholder_text=placeholder or "",
            **kwargs,
        )
        return widget

    widget = tk.Entry(
        master,
        bg=colors.surface,
        fg=colors.text,
        highlightbackground=colors.border,
        highlightthickness=1,
        bd=0,
        **kwargs,
    )
    widget.configure(**size_tokens)
    return widget
