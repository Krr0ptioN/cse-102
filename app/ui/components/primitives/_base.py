from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional dependency
    ctk = None

from app.design_system.semantic_tokens import semantic_colors


def use_ctk(master=None) -> bool:
    if ctk is None:
        return False
    ui_mode = os.getenv("APP_UI", "ctk").lower()
    if ui_mode == "ctk":
        return True
    if master is None:
        return False
    try:
        return isinstance(master, ctk.CTkBaseClass)
    except Exception:
        return False


def tk_style(master) -> ttk.Style:
    style = ttk.Style(master)
    colors = semantic_colors()
    style.configure(
        "Ds.TCombobox",
        fieldbackground=colors.surface,
        background=colors.surface,
        foreground=colors.text,
        bordercolor=colors.border,
    )
    style.configure(
        "Ds.Treeview",
        background=colors.surface,
        fieldbackground=colors.surface,
        foreground=colors.text,
        bordercolor=colors.border,
    )
    style.configure(
        "Ds.Treeview.Heading",
        background=colors.panel,
        foreground=colors.text,
    )
    return style


def frame_bg_kwargs(*, panel: bool = False) -> dict[str, str]:
    colors = semantic_colors()
    return {"bg": colors.panel if panel else colors.bg}
