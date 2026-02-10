from __future__ import annotations

import tkinter as tk

from app.ui.theme import palette


class StatCard(tk.Frame):
    def __init__(self, master, label: str, value: str) -> None:
        colors = palette()
        super().__init__(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
        )
        self.label = tk.Label(
            self,
            text=label,
            font=("Segoe UI", 9),
            bg=colors["panel"],
            fg=colors["muted"],
        )
        self.label.pack(anchor="w", padx=8, pady=(6, 0))
        self.value = tk.Label(
            self,
            text=value,
            font=("Segoe UI", 14, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
        )
        self.value.pack(anchor="w", padx=8, pady=(0, 6))

    def set_value(self, value: str) -> None:
        self.value.config(text=value)


class DetailsDrawer(tk.Frame):
    def __init__(self, master, title: str) -> None:
        colors = palette()
        super().__init__(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
            width=260,
        )
        self.pack_propagate(False)
        tk.Label(
            self,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
        ).pack(anchor="w", padx=12, pady=(12, 6))
        self.body = tk.Frame(self, bg=colors["panel"])
        self.body.pack(fill="both", expand=True, padx=12, pady=6)
        self.actions = tk.Frame(self, bg=colors["panel"])
        self.actions.pack(fill="x", padx=12, pady=(0, 12))

    def clear(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()
        for child in self.actions.winfo_children():
            child.destroy()
