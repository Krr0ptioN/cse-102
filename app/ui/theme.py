from __future__ import annotations

import tkinter as tk
from tkinter import ttk


def apply_theme(root: tk.Tk) -> None:
    colors = {
        "bg": "#f7f5f0",
        "panel": "#ffffff",
        "border": "#d9d2c4",
        "text": "#1d1b17",
        "muted": "#6a6256",
        "accent": "#1f3a5f",
        "accent_light": "#e0e6ef",
    }

    root.configure(bg=colors["bg"])

    root.option_add("*Background", colors["bg"])
    root.option_add("*Foreground", colors["text"])
    root.option_add("*Entry.Background", colors["panel"])
    root.option_add("*Entry.Foreground", colors["text"])
    root.option_add("*Text.Background", colors["panel"])
    root.option_add("*Text.Foreground", colors["text"])
    root.option_add("*Listbox.Background", colors["panel"])
    root.option_add("*Listbox.Foreground", colors["text"])
    root.option_add("*Button.Background", colors["accent_light"])
    root.option_add("*Button.Foreground", colors["accent"])
    root.option_add("*Button.ActiveBackground", colors["accent"])
    root.option_add("*Button.ActiveForeground", "#ffffff")

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        "TFrame",
        background=colors["bg"],
    )
    style.configure(
        "TLabel",
        background=colors["bg"],
        foreground=colors["text"],
    )
    style.configure(
        "TButton",
        background=colors["accent_light"],
        foreground=colors["accent"],
        bordercolor=colors["border"],
        focusthickness=3,
        focuscolor=colors["accent"],
        padding=(8, 4),
    )
    style.map(
        "TButton",
        background=[("active", colors["accent"])],
        foreground=[("active", "#ffffff")],
    )
    style.configure(
        "TLabelframe",
        background=colors["bg"],
        foreground=colors["text"],
        bordercolor=colors["border"],
    )
    style.configure(
        "TLabelframe.Label",
        background=colors["bg"],
        foreground=colors["accent"],
        font=("Helvetica", 11, "bold"),
    )
    style.configure(
        "Treeview",
        background=colors["panel"],
        fieldbackground=colors["panel"],
        foreground=colors["text"],
        bordercolor=colors["border"],
        rowheight=22,
    )
    style.map(
        "Treeview",
        background=[("selected", colors["accent_light"])],
        foreground=[("selected", colors["accent"])],
    )
    style.configure(
        "TCombobox",
        fieldbackground=colors["panel"],
        background=colors["panel"],
        foreground=colors["text"],
    )
