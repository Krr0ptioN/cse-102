from __future__ import annotations

import os
import tkinter as tk
from tkinter import ttk

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional dependency
    ctk = None

from libs.ui_kit.design_system import semantic_colors
from libs.ui_kit.design_system import Typography


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

    body_font = (Typography.primary_font_family(), 10)
    heading_font = (Typography.primary_font_family(), 10, "bold")

    style.configure(
        "Ds.TCombobox",
        fieldbackground=colors.surface,
        background=colors.surface,
        foreground=colors.text,
        bordercolor=colors.border,
        arrowsize=14,
        padding=6,
        font=body_font,
    )
    style.configure(
        "Ds.Treeview",
        background=colors.surface,
        fieldbackground=colors.surface,
        foreground=colors.text,
        bordercolor=colors.border,
        rowheight=30,
        borderwidth=1,
        relief="solid",
        font=body_font,
    )
    style.configure(
        "Ds.Treeview.Heading",
        background=colors.panel,
        foreground=colors.text,
        bordercolor=colors.border,
        relief="flat",
        padding=(10, 8),
        font=heading_font,
    )
    style.map(
        "Ds.Treeview",
        background=[("selected", colors.primary_soft)],
        foreground=[("selected", colors.text)],
    )
    style.map(
        "Ds.Treeview.Heading",
        background=[("active", colors.surface)],
        foreground=[("active", colors.text)],
    )
    return style


def frame_bg_kwargs(*, panel: bool = False) -> dict[str, str]:
    colors = semantic_colors()
    return {"bg": colors.panel if panel else colors.bg}
