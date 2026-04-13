from __future__ import annotations

import tkinter as tk
from tkinter import ttk, font as tkfont

from app.libs.ui_kit.design_system.tokens import palette as design_palette
from app.libs.ui_kit.design_system.typography import Typography


def palette() -> dict[str, str]:
    # Bridge to legacy callers expecting a dict.
    p = design_palette()
    return {
        "bg": p.bg,
        "panel": p.panel,
        "sidebar": p.surface,
        "border": p.border,
        "text": p.text,
        "muted": p.muted,
        "accent": p.primary,
        "accent_light": "#e8efff",
    }


def apply_theme(root: tk.Tk) -> None:
    colors = palette()

    Typography.ensure_tk_font(root)

    _apply_default_fonts(root)

    root.configure(bg=colors["bg"])

    root.option_add("*Font", f"{Typography.primary_font_family()} 10")
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

    default_family = Typography.primary_font_family()
    style.configure(".", font=(default_family, 10))

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
        font=(Typography.primary_font_family(), 10),
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
        font=(Typography.primary_font_family(), 11, "bold"),
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


def _apply_default_fonts(root: tk.Tk) -> None:
    """Apply the primary family to Tk default named fonts."""

    family = Typography.primary_font_family()
    for name, size in (
        ("TkDefaultFont", 10),
        ("TkTextFont", 10),
        ("TkMenuFont", 10),
    ):
        try:
            f = tkfont.nametofont(name)
            f.configure(family=family, size=size)
        except Exception:
            continue
