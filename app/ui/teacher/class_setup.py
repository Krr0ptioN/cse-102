from __future__ import annotations

import tkinter as tk

from app.ui.components import Section
from app.ui.forms import ClassForm


class ClassSetupSection(Section):
    def __init__(self, master, on_create) -> None:
        super().__init__(master, "Class Setup")
        self.on_create = on_create
        self.form = ClassForm()
        self._build()

    def _build(self) -> None:
        self.form.render(self.body, columns=2)
        tk.Button(self.body, text="Create Class", command=self.on_create).grid(
            row=0, column=2, padx=6, pady=16
        )

        self.status = tk.Label(self.body, text="No class selected")
        self.status.grid(row=1, column=0, columnspan=3, sticky="w")

    def get_name(self) -> str:
        return self.form.get_data()["name"]

    def get_term(self) -> str:
        return self.form.get_data()["term"]

    def clear(self) -> None:
        self.form.clear()

    def errors(self) -> list[str]:
        return self.form.validate()

    def set_status(self, text: str) -> None:
        self.status.config(text=text)
