from __future__ import annotations

import tkinter as tk

from ...design_system import button_size_tokens, button_variants
from ...design_system import resolve_variant
from ._base import ctk, use_ctk


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
        kwargs.setdefault("text", text)
        kwargs.setdefault("command", command)
        kwargs.setdefault("fg_color", variant_tokens.bg)
        kwargs.setdefault("hover_color", variant_tokens.hover)
        kwargs.setdefault("text_color", variant_tokens.fg)
        kwargs.setdefault("border_color", variant_tokens.border)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("corner_radius", 0)
        
        # Filter standard tk keys
        if "bg" in kwargs:
            kwargs.setdefault("fg_color", kwargs.pop("bg"))
        if "fg" in kwargs:
            kwargs.setdefault("text_color", kwargs.pop("fg"))
            
        return ctk.CTkButton(master, **kwargs)

    kwargs.setdefault("text", text)
    kwargs.setdefault("command", command)
    kwargs.setdefault("bg", variant_tokens.bg)
    kwargs.setdefault("fg", variant_tokens.fg)
    kwargs.setdefault("activebackground", variant_tokens.hover)
    kwargs.setdefault("activeforeground", variant_tokens.fg)
    kwargs.setdefault("highlightbackground", variant_tokens.border)
    kwargs.setdefault("relief", "ridge")
    kwargs.setdefault("bd", 1)

    button = tk.Button(master, **kwargs)
    button.configure(padx=size_tokens["padx"], pady=size_tokens["pady"])
    return button


def set_button_variant(button, variant: str, size: str = "md") -> None:
    """Safely update a button's variant and size styles."""
    _, variant_tokens = resolve_variant(variant, button_variants(), default="default")
    _, size_tokens = resolve_variant(size, button_size_tokens(), default="md")

    if ctk is not None and isinstance(button, ctk.CTkButton):
        button.configure(
            fg_color=variant_tokens.bg,
            hover_color=variant_tokens.hover,
            text_color=variant_tokens.fg,
            border_color=variant_tokens.border,
        )
    else:
        button.configure(
            bg=variant_tokens.bg,
            fg=variant_tokens.fg,
            activebackground=variant_tokens.hover,
            activeforeground=variant_tokens.fg,
            highlightbackground=variant_tokens.border,
            padx=size_tokens["padx"],
            pady=size_tokens["pady"],
        )
