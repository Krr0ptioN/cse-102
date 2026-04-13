from __future__ import annotations

import os
import tkinter as tk

from app.libs.ui_kit.design_system.typography import Typography

try:
    import customtkinter as ctk
    from app.libs.ui_kit.design.theme import apply_ctk_theme
except Exception:  # pragma: no cover - fallback when CTk unavailable
    ctk = None
    apply_ctk_theme = None  # type: ignore

try:
    from app.libs.ui_kit.theme import apply_theme as apply_tk_theme
except Exception:  # pragma: no cover
    apply_tk_theme = None  # type: ignore


def resolve_root_class():
    Typography.bootstrap_fonts()
    ui_mode = os.getenv("APP_UI", "ctk").lower()
    if ctk is not None and ui_mode == "ctk":
        return ctk.CTk
    return tk.Tk


def apply_root_theme(root) -> None:
    if ctk is not None and isinstance(root, ctk.CTk) and apply_ctk_theme:
        apply_ctk_theme(root)
        # Keep legacy Tk/ttk widgets styled in mixed CTk+Tk screens.
        if apply_tk_theme is not None:
            apply_tk_theme(root)
    elif apply_tk_theme is not None:
        apply_tk_theme(root)
