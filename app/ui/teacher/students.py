from __future__ import annotations

import tkinter as tk

from app.ui.components import ButtonBar, DataTable, Section
from app.ui.forms import StudentForm


class StudentRosterSection(Section):
    def __init__(self, master, on_add, on_edit, on_delete, on_select) -> None:
        super().__init__(master, "Student Roster")
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_select = on_select
        self.form = StudentForm()
        self._build()

    def _build(self) -> None:
        form = tk.Frame(self.body)
        form.pack(fill="x", pady=6)
        self.form.render(form, columns=2)
        tk.Button(form, text="Add Student", command=self.on_add).grid(
            row=0, column=2, padx=6, pady=16
        )

        toolbar = ButtonBar(self.body)
        toolbar.pack(fill="x", pady=6)
        toolbar.add("Edit", self.on_edit)
        toolbar.add("Delete", self.on_delete)

        self.table = DataTable(self.body, ["Id", "Name", "Email"], height=6)
        self.table.pack(fill="both", expand=True, pady=6)
        self.table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

    def get_name(self) -> str:
        return self.form.get_data()["name"]

    def get_email(self) -> str:
        return self.form.get_data()["email"]

    def clear_form(self) -> None:
        self.form.clear()

    def errors(self) -> list[str]:
        return self.form.validate()

    def set_rows(self, rows: list[tuple]) -> None:
        self.table.set_rows(rows)

    def selected_id(self) -> int | None:
        selection = self.table.selection()
        if not selection:
            return None
        return int(self.table.item(selection[0], "values")[0])

    def selected_row(self) -> tuple | None:
        selection = self.table.selection()
        if not selection:
            return None
        return self.table.item(selection[0], "values")
