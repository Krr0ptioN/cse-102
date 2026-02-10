from __future__ import annotations

import tkinter as tk

from app.ui.components import StatCard


class StudentStatsRow(tk.Frame):
    def __init__(self, master) -> None:
        super().__init__(master)
        self.grid_columnconfigure((0, 1), weight=1)
        self.status = StatCard(self, "Roadmap Status", "-")
        self.status.grid(row=0, column=0, padx=8, sticky="ew")
        self.done = StatCard(self, "Tasks Done", "0")
        self.done.grid(row=0, column=1, padx=8, sticky="ew")

    def set_values(self, status: str, done: int) -> None:
        self.status.set_value(status)
        self.done.set_value(str(done))
