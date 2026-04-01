from __future__ import annotations

import tkinter as tk

from app.design_system.component_tokens import button_size_tokens, button_variants
from app.design_system.variants import resolve_variant
from app.ui.components.primitives._base import ctk, use_ctk


BUTTON_VARIANTS = tuple(button_variants().keys())
BUTTON_SIZES = tuple(button_size_tokens().keys())


def Button(  # noqa: N802
    master,
    *,
    text: str,
    command=None,
    variant: str = "default",
    size: str = "md",
    **kwargs,
):
    _, variant_tokens = resolve_variant(variant, button_variants(), default="default")
    _, size_tokens = resolve_variant(size, button_size_tokens(), default="md")

    if use_ctk(master) and ctk is not None:
        return ctk.CTkButton(
            master,
            text=text,
            command=command,
            fg_color=variant_tokens.bg,
            hover_color=variant_tokens.hover,
            text_color=variant_tokens.fg,
            border_color=variant_tokens.border,
            border_width=1,
            corner_radius=0,
            **kwargs,
        )

    button = tk.Button(
        master,
        text=text,
        command=command,
        bg=variant_tokens.bg,
        fg=variant_tokens.fg,
        activebackground=variant_tokens.hover,
        activeforeground=variant_tokens.fg,
        highlightbackground=variant_tokens.border,
        relief="ridge",
        bd=1,
        **kwargs,
    )
    button.configure(padx=size_tokens["padx"], pady=size_tokens["pady"])
    return button
