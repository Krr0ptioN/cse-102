from __future__ import annotations

import tkinter as tk

from app.design_system.tokens import palette
from app.design_system.typography import Typography


FONT_FAMILY = Typography.primary_font_family()


class PageHeader(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(master, bg=colors.bg)
        self.label = tk.Label(
            self,
            text=title,
            font=(FONT_FAMILY, 16, "bold"),
            bg=colors.bg,
            fg=colors.text,
        )
        self.label.pack(side="left", padx=6, pady=8)

    def set_title(self, title: str) -> None:
        self.label.config(text=title)


class Sidebar(tk.Frame):
    def __init__(self, master, items: list[tuple[str, str]], on_select) -> None:
        colors = palette()
        super().__init__(master, width=220, bg=colors.panel)
        self.pack_propagate(False)
        self.on_select = on_select
        for key, label in items:
            btn = tk.Button(
                self,
                text=label,
                anchor="w",
                bg=colors.panel,
                fg=colors.text,
                relief="flat",
                command=lambda k=key: on_select(k),
            )
            btn.pack(fill="x", padx=8, pady=4)
