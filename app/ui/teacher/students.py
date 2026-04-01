from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.ui.components import (
    Button,
    ButtonBar,
    DataTable,
    Modal,
    Section,
    bind_modal_keys,
)
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
        toolbar = ButtonBar(self.body)
        toolbar.pack(fill="x", pady=6)
        toolbar.add("Add", self._open_add_modal)
        toolbar.add("Edit", self._open_edit_modal)
        toolbar.add("Delete", self._open_delete_modal)

        self.table = DataTable(self.body, ["Id", "Name", "Email"], height=8)
        self.table.pack(fill="both", expand=True, pady=6)
        self.table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

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

    # ----- Modal helpers -------------------------------------------------

    def _open_add_modal(self) -> None:
        modal = Modal(self, "Add Student")
        form = StudentForm()
        form.render(modal.body, columns=2)

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            modal.destroy()
            self.on_add(data)

        bind_modal_keys(modal, save)
        Button(
            modal.actions, text="Cancel", command=modal.destroy, variant="outline"
        ).pack(side="right", padx=4)
        Button(modal.actions, text="Save", command=save, size="sm").pack(
            side="right", padx=4
        )

    def _open_edit_modal(self) -> None:
        row = self.selected_row()
        if not row:
            tk.messagebox.showwarning("No student", "Select a student first.")
            return
        modal = Modal(self, "Edit Student")
        form = StudentForm()
        form.render(modal.body, columns=2)
        form.set_data({"name": row[1], "email": row[2]})

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            modal.destroy()
            self.on_edit(int(row[0]), data)

        bind_modal_keys(modal, save)
        Button(
            modal.actions, text="Cancel", command=modal.destroy, variant="outline"
        ).pack(side="right", padx=4)
        Button(modal.actions, text="Save", command=save, size="sm").pack(
            side="right", padx=4
        )

    def _open_delete_modal(self) -> None:
        row = self.selected_row()
        if not row:
            messagebox.showwarning("No student", "Select a student first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {row[1]}?"):
            return
        self.on_delete(int(row[0]))
