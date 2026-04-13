from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.ui.components import (
    Button,
    ButtonBar,
    Card,
    DataTable,
    Input,
    Label,
    Modal,
    SectionHeader,
    add_modal_actions,
)
from app.ui.forms import StudentForm
from app.ui.theme import palette


class StudentRosterSection(tk.Frame):
    def __init__(self, master, on_add, on_edit, on_delete, on_select) -> None:
        colors_bg = (
            master["bg"] if isinstance(master, tk.BaseWidget) else palette()["bg"]
        )
        super().__init__(master, bg=colors_bg)
        self.on_add = on_add
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_select = on_select
        self.form = StudentForm()
        self._row_count = 0
        self._build()

    def _build(self) -> None:
        header = SectionHeader(
            self,
            title="Student Roster",
            subtitle="Create, update, and remove student accounts for this class.",
        )
        header.pack(fill="x", padx=12, pady=(12, 8))

        actions_card = Card(self)
        actions_card.pack(fill="x", padx=12, pady=(0, 8))
        toolbar = ButtonBar(actions_card)
        toolbar.pack(fill="x", padx=12, pady=12)
        toolbar.add("Add Student", self._open_add_modal)
        toolbar.add("Edit", self._open_edit_modal)
        toolbar.add("Delete", self._open_delete_modal)

        table_card = Card(self)
        table_card.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        Label(table_card, text="Students", weight="bold").pack(
            anchor="w", padx=12, pady=(12, 6)
        )

        self.student_filter_var = tk.StringVar(value="")
        filter_row = tk.Frame(table_card, bg=table_card["bg"])
        filter_row.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(filter_row, text="Filter", bg=table_card["bg"]).pack(side="left")
        self.student_filter_entry = Input(
            filter_row,
            width=30,
            textvariable=self.student_filter_var,
        )
        self.student_filter_entry.pack(side="left", padx=(8, 8))
        self.student_filter_entry.bind(
            "<KeyRelease>",
            lambda _e: self._apply_student_filter(),
        )
        Button(
            filter_row,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_student_filter,
        ).pack(side="left")

        self.table = DataTable(table_card, ["Id", "Name", "Email"], height=11)
        self.table.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.table.bind("<<TreeviewSelect>>", lambda _e: self.on_select())

        self.count_label = Label(table_card, text="0 students", variant="muted")
        self.count_label.pack(anchor="w", padx=12, pady=(0, 12))

    def set_rows(self, rows: list[tuple]) -> None:
        self._row_count = len(rows)
        self.table.set_rows(rows)
        self._apply_student_filter()

    def selected_id(self) -> int | None:
        selection = self.table.selection()
        if not selection:
            return None
        values = self.table.item(selection[0], "values")
        if not values:
            return None
        try:
            return int(values[0])
        except (TypeError, ValueError):
            return None

    def selected_row(self) -> tuple | None:
        selection = self.table.selection()
        if not selection:
            return None
        return self.table.item(selection[0], "values")

    def _apply_student_filter(self) -> None:
        query = self.student_filter_var.get().strip()
        self.table.apply_filter(query, columns=(1, 2))
        visible = len(self.table.get_children())
        self._update_count_label(visible)

    def _clear_student_filter(self) -> None:
        self.student_filter_var.set("")
        self._apply_student_filter()

    def _update_count_label(self, visible_count: int) -> None:
        suffix = "student" if self._row_count == 1 else "students"
        if visible_count == self._row_count:
            self.count_label.configure(text=f"{self._row_count} {suffix}")
            return
        self.count_label.configure(
            text=f"{visible_count} of {self._row_count} {suffix}"
        )

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

        add_modal_actions(modal, save, confirm_text="Save")

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

        add_modal_actions(modal, save, confirm_text="Save")

    def _open_delete_modal(self) -> None:
        row = self.selected_row()
        if not row:
            messagebox.showwarning("No student", "Select a student first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete {row[1]}?"):
            return
        self.on_delete(int(row[0]))
