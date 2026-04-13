from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.libs.ui_kit.theme import palette


class LabeledEntry(tk.Frame):
    def __init__(self, master, label: str, width: int = 20) -> None:
        colors = palette()
        super().__init__(master, bg=colors["panel"])
        self.label = tk.Label(self, text=label, bg=colors["panel"], fg=colors["muted"])
        self.entry = tk.Entry(self, width=width)
        self.label.grid(row=0, column=0, sticky="w")
        self.entry.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def get(self) -> str:
        return self.entry.get()

    def set(self, value: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, value)

    def clear(self) -> None:
        self.entry.delete(0, tk.END)


class LabeledCombobox(tk.Frame):
    def __init__(self, master, label: str, width: int = 20) -> None:
        colors = palette()
        super().__init__(master, bg=colors["panel"])
        self.label = tk.Label(self, text=label, bg=colors["panel"], fg=colors["muted"])
        self.combo = ttk.Combobox(self, width=width, state="readonly")
        self.label.grid(row=0, column=0, sticky="w")
        self.combo.grid(row=1, column=0, sticky="w", pady=(2, 0))

    def set_values(self, values: list[str]) -> None:
        self.combo["values"] = values

    def get(self) -> str:
        return self.combo.get()

    def clear(self) -> None:
        self.combo.set("")
