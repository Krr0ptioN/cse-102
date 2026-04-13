from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.components import Button, Card, Input, Label, Section, SectionHeader


class ClassSetupSection(Section):
    def __init__(self, master, on_create) -> None:
        super().__init__(master, "Class Setup")
        self.on_create = on_create
        self._build()

    def _build(self) -> None:
        card = Card(self.body)
        card.pack(fill="x", padx=4, pady=4)

        SectionHeader(
            card,
            title="Create Class",
            subtitle="Set the class name and term before managing students and teams.",
        ).pack(fill="x", padx=10, pady=(8, 2))

        form_row = tk.Frame(card, bg=card["bg"])
        form_row.pack(fill="x", padx=10, pady=(2, 10))

        tk.Label(form_row, text="Class Name", bg=card["bg"]).grid(
            row=0, column=0, sticky="w"
        )
        self.name_entry = Input(form_row, width=28)
        self.name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(2, 0))

        tk.Label(form_row, text="Term", bg=card["bg"]).grid(row=0, column=1, sticky="w")
        self.term_entry = Input(form_row, width=20)
        self.term_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(2, 0))

        Button(form_row, text="Create Class", command=self.on_create, size="sm").grid(
            row=1, column=2, padx=0, pady=(2, 0), sticky="ew"
        )
        form_row.columnconfigure(0, weight=3)
        form_row.columnconfigure(1, weight=2)
        form_row.columnconfigure(2, minsize=112)

        self.status = Label(self.body, text="No class selected", variant="muted")
        self.status.pack(anchor="w", padx=8, pady=(4, 2))

    def get_name(self) -> str:
        return self.name_entry.get().strip()

    def get_term(self) -> str:
        return self.term_entry.get().strip()

    def clear(self) -> None:
        self.name_entry.delete(0, tk.END)
        self.term_entry.delete(0, tk.END)

    def errors(self) -> list[str]:
        errors: list[str] = []
        name = self.get_name()
        term = self.get_term()
        if not name:
            errors.append("Class Name: required")
        elif len(name) > 50:
            errors.append("Class Name: must be 50 characters or fewer")

        if not term:
            errors.append("Term: required")
        elif len(term) > 20:
            errors.append("Term: must be 20 characters or fewer")

        return errors

    def set_status(self, text: str) -> None:
        self.status.config(text=text)
