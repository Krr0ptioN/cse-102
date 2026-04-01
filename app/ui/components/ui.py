from __future__ import annotations

import os
import tkinter as tk

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional
    ctk = None

from app.ui.components.adapters import is_ctk
from app.ui.components.ctk_primitives import (
    CtkButton,
    CtkInput,
    CtkCard,
    CtkModal,
    CtkProgress,
)
from app.ui.components.layout import Section as TkSection
from app.ui.components.modals import Modal as TkModal
from app.ui.components.actions import ButtonBar as TkButtonBar
from app.ui.theme import palette


def Button(master, **kwargs):  # noqa: N802 - factory style
    if is_ctk():
        return CtkButton(master, **kwargs)
    colors = palette()
    base_kwargs = {
        "bg": colors["accent_light"],
        "fg": colors["text"],
        "activebackground": colors["accent"],
        "activeforeground": "#ffffff",
        "bd": 1,
        "relief": "ridge",
        "padx": 8,
        "pady": 4,
    }
    base_kwargs.update(kwargs)
    return tk.Button(master, **base_kwargs)


def Input(master, **kwargs):  # noqa: N802
    if is_ctk():
        return CtkInput(master, **kwargs)
    colors = palette()
    base_kwargs = {
        "bg": colors["surface"],
        "fg": colors["text"],
        "highlightbackground": colors["border"],
        "highlightthickness": 1,
        "bd": 0,
    }
    base_kwargs.update(kwargs)
    return tk.Entry(master, **base_kwargs)


def Card(master, **kwargs):  # noqa: N802
    if is_ctk():
        return CtkCard(master, **kwargs)
    colors = palette()
    base_kwargs = {
        "bg": colors["panel"],
        "highlightbackground": colors["border"],
        "highlightthickness": 1,
        "bd": 0,
    }
    base_kwargs.update(kwargs)
    return tk.Frame(master, **base_kwargs)


def Progress(master, **kwargs):  # noqa: N802
    if is_ctk():
        return CtkProgress(master, **kwargs)
    from tkinter import ttk

    colors = palette()
    bar = ttk.Progressbar(master, orient="horizontal", mode="determinate", **kwargs)
    style = ttk.Style(bar)
    style.configure(
        "Custom.Horizontal.TProgressbar",
        background=colors["accent"],
        troughcolor=colors["panel"],
    )
    bar.configure(style="Custom.Horizontal.TProgressbar")
    return bar


def Modal(master, title: str):  # noqa: N802
    if is_ctk():
        return CtkModal(master, title)
    return TkModal(master, title)


def Section(master, title: str, subtitle: str | None = None):  # noqa: N802
    return TkSection(master, title, subtitle)


def ButtonBar(master):  # noqa: N802
    return TkButtonBar(master)
