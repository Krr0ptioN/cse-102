from __future__ import annotations

import tkinter as tk
from tkinter import ttk


PALETTE = {
        "bg": "#f2f4f3",
        "panel": "#ffffff",
        "sidebar": "#e8eceb",
        "border": "#cfd8d5",
        "text": "#1b1f1e",
        "muted": "#5f6b68",
        "accent": "#0f766e",
        "accent_light": "#dff3f1",
}


def palette() -> dict[str, str]:
    return dict(PALETTE)


def apply_theme(root: tk.Tk) -> None:
    colors = PALETTE

    root.configure(bg=colors["bg"])

    root.option_add("*Font", "{Segoe UI} 10")
    root.option_add("*Background", colors["bg"])
    root.option_add("*Foreground", colors["text"])
    root.option_add("*Frame.Background", colors["bg"])
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

    style.configure("TFrame", background=colors["bg"])
    style.configure("TLabel", background=colors["bg"], foreground=colors["text"])
    style.configure(
        "TButton",
        background=colors["accent_light"],
        foreground=colors["accent"],
        bordercolor=colors["border"],
        focusthickness=2,
        focuscolor=colors["accent"],
        padding=(10, 6),
    )
    style.map(
        "TButton",
        background=[("active", colors["accent"])],
        foreground=[("active", "#ffffff")],
    )
    style.configure("TLabelframe", background=colors["bg"], foreground=colors["text"])
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
        rowheight=26,
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

    style.configure("Sidebar.TFrame", background=colors["sidebar"])
    style.configure("Card.TFrame", background=colors["panel"])
    style.configure("Topbar.TFrame", background=colors["panel"])
