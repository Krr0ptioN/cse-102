from __future__ import annotations

import tkinter as tk

from app.design_system.component_tokens import card_tokens
from app.ui.components.primitives._base import ctk, use_ctk


def Card(  # noqa: N802
    master,
    *,
    variant: str = "default",
    **kwargs,
):
    del variant  # reserved for future variants
    tokens = card_tokens()
    if use_ctk(master) and ctk is not None:
        return ctk.CTkFrame(
            master,
            fg_color=tokens["bg"],
            border_color=tokens["border"],
            border_width=1,
            corner_radius=tokens["radius"],
            **kwargs,
        )
    return tk.Frame(
        master,
        bg=tokens["bg"],
        highlightbackground=tokens["border"],
        highlightthickness=1,
        bd=0,
        **kwargs,
    )
