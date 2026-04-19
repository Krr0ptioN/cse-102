from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import Typography
from libs.ui_kit.theme import palette


class Modal(tk.Toplevel):
    def __init__(self, master, title: str) -> None:
        super().__init__(master)
        colors = palette()
        self.title(title)
        self.configure(bg=colors["panel"])
        self.resizable(False, False)
        self.transient(master)
        self.wait_visibility()
        self.grab_set()

        self.header = tk.Label(
            self,
            text=title,
            font=(Typography.primary_font_family(), 12, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
        )
        self.header.pack(anchor="w", padx=16, pady=(16, 8))

        self.body = tk.Frame(self, bg=colors["panel"])
        self.body.pack(fill="both", expand=True, padx=16, pady=8)

        self.actions = tk.Frame(self, bg=colors["panel"])
        self.actions.pack(fill="x", padx=16, pady=(0, 16))
