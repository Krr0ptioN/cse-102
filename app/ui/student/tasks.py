from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.libs.ui_kit.components import Button, ButtonBar, DataTable, Section


class TaskSection(Section):
    def __init__(self, master, on_select_task, on_set_status, on_add_update) -> None:
        super().__init__(master, "Tasks")
        self.on_select_task = on_select_task
        self.on_set_status = on_set_status
        self.on_add_update = on_add_update
        self._build()

    def _build(self) -> None:
        self.task_table = DataTable(
            self.body, ["Id", "Task", "Status", "Weight"], height=7
        )
        self.task_table.pack(fill="both", expand=True, pady=6)
        self.task_table.bind("<<TreeviewSelect>>", lambda _e: self.on_select_task())

        actions = ButtonBar(self.body)
        actions.pack(fill="x", pady=4)
        actions.add("In Progress", lambda: self.on_set_status("In Progress"))
        actions.add("Done", lambda: self.on_set_status("Done"))

        member_row = tk.Frame(self.body)
        member_row.pack(fill="x", pady=4)
        tk.Label(member_row, text="Update as").pack(side="left", padx=4)
        self.member_select = ttk.Combobox(member_row, state="readonly")
        self.member_select.pack(side="left", padx=4)

        self.update_text = tk.Text(self.body, height=4)
        self.update_text.pack(fill="x", pady=6)
        Button(
            self.body, text="Add Update", command=self.on_add_update, size="sm"
        ).pack(anchor="e")

        self.update_table = DataTable(self.body, ["User", "Update", "Time"], height=6)
        self.update_table.pack(fill="both", expand=True, pady=6)

    def set_task_rows(self, rows: list[tuple]) -> None:
        self.task_table.set_rows(rows)

    def set_update_rows(self, rows: list[tuple]) -> None:
        self.update_table.set_rows(rows)

    def set_member_choices(self, values: list[str]) -> None:
        self.member_select["values"] = values

    def selected_task_id(self) -> int | None:
        selection = self.task_table.selection()
        if not selection:
            return None
        return int(self.task_table.item(selection[0], "values")[0])

    def selected_member_label(self) -> str:
        return self.member_select.get()

    def get_update_text(self) -> str:
        return self.update_text.get("1.0", tk.END).strip()

    def clear_update_text(self) -> None:
        self.update_text.delete("1.0", tk.END)
