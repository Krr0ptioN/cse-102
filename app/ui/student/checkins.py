from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.libs.ui_kit import ButtonBar, DataTable, Section
from app.ui.student.forms import CheckinForm


class StudentCheckinsSection(Section):
    def __init__(self, master, on_submit) -> None:
        super().__init__(master, "Weekly Check-ins")
        self.on_submit = on_submit
        self.form = CheckinForm()
        self._build()

    def _build(self) -> None:
        progress_row = tk.Frame(self.body)
        progress_row.pack(fill="x", pady=4)
        tk.Label(progress_row, text="Progress").pack(side="left", padx=4)
        self.progress = ttk.Progressbar(
            progress_row, orient="horizontal", length=180, mode="determinate"
        )
        self.progress.pack(side="left", padx=6)
        self.progress_label = tk.Label(progress_row, text="0%")
        self.progress_label.pack(side="left", padx=4)

        self.metrics_label = tk.Label(self.body, text="0/0 tasks done")
        self.metrics_label.pack(anchor="w", padx=4, pady=(2, 8))

        form = tk.Frame(self.body)
        form.pack(fill="x", pady=4)
        self.form.render(form, columns=1)
        status_field = self.form.get_field("status")
        if status_field and hasattr(status_field, "set_values"):
            status_field.set_values(["Green", "Yellow", "Red"])

        actions = ButtonBar(self.body)
        actions.pack(fill="x", pady=6)
        actions.add("Submit Check-in", self.on_submit)

        self.table = DataTable(
            self.body,
            ["Id", "Week", "Status", "Progress", "Submitted"],
            height=6,
        )
        self.table.pack(fill="both", expand=True, pady=6)

    def set_progress(self, percent: int, done: int, total: int) -> None:
        self.progress["value"] = percent
        self.progress_label.config(text=f"{percent}%")
        self.metrics_label.config(text=f"{done}/{total} tasks done")

    def get_data(self) -> dict:
        return self.form.get_data()

    def clear_form(self) -> None:
        self.form.clear()

    def errors(self) -> list[str]:
        return self.form.validate()

    def set_rows(self, rows: list[tuple]) -> None:
        self.table.set_rows(rows)
