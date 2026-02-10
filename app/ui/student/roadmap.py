from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.ui.components import ButtonBar, LabeledCombobox, LabeledEntry, Section
from app.ui.forms import TaskForm


class RoadmapBuilderSection(Section):
    def __init__(
        self,
        master,
        on_student_change,
        on_invite_accept,
        on_invite_decline,
        on_team_change,
        on_add_phase,
        on_edit_phase,
        on_delete_phase,
        on_add_task,
        on_edit_task,
        on_delete_task,
        on_submit,
        on_charts,
    ) -> None:
        super().__init__(master, "Roadmap Builder")
        self._callbacks = {
            "student_change": on_student_change,
            "invite_accept": on_invite_accept,
            "invite_decline": on_invite_decline,
            "team_change": on_team_change,
            "add_phase": on_add_phase,
            "edit_phase": on_edit_phase,
            "delete_phase": on_delete_phase,
            "add_task": on_add_task,
            "edit_task": on_edit_task,
            "delete_task": on_delete_task,
            "submit": on_submit,
            "charts": on_charts,
        }
        self.task_form = TaskForm()
        self._build()

    def _build(self) -> None:
        student_row = tk.Frame(self.body)
        student_row.pack(fill="x", pady=4)
        student_field = LabeledCombobox(student_row, "Student", width=28)
        student_field.pack(side="left", padx=4)
        self.student_select = student_field.combo
        self.student_select.bind("<<ComboboxSelected>>", lambda _e: self._callbacks["student_change"]())

        invite_block = tk.Frame(self.body)
        invite_block.pack(fill="x", pady=4)
        tk.Label(invite_block, text="Invitations").pack(anchor="w")
        self.invite_table = ttk.Treeview(invite_block, columns=("Id", "Team", "Status"), show="headings", height=3)
        for col in ("Id", "Team", "Status"):
            self.invite_table.heading(col, text=col)
            self.invite_table.column(col, anchor="w", width=120, stretch=True)
        self.invite_table.pack(fill="x", pady=4)
        invite_actions = ButtonBar(invite_block)
        invite_actions.pack(fill="x")
        invite_actions.add("Accept", self._callbacks["invite_accept"])
        invite_actions.add("Decline", self._callbacks["invite_decline"])

        selector = tk.Frame(self.body)
        selector.pack(fill="x", pady=4)
        team_field = LabeledCombobox(selector, "Team", width=34)
        team_field.pack(side="left", padx=4)
        self.team_select = team_field.combo
        self.team_select.bind("<<ComboboxSelected>>", lambda _e: self._callbacks["team_change"]())

        controls = tk.Frame(self.body)
        controls.pack(fill="x", pady=6)

        phase_field = LabeledEntry(controls, "Phase Name", width=20)
        phase_field.grid(row=0, column=0, padx=4, sticky="w")
        tk.Button(controls, text="Add Phase", command=self._callbacks["add_phase"]).grid(
            row=0, column=1, padx=4, pady=16
        )
        tk.Button(controls, text="Edit Phase", command=self._callbacks["edit_phase"]).grid(
            row=0, column=2, padx=4, pady=16
        )
        tk.Button(controls, text="Delete Phase", command=self._callbacks["delete_phase"]).grid(
            row=0, column=3, padx=4, pady=16
        )

        self.task_form.render(controls, columns=2, start_row=1)
        tk.Button(controls, text="Add Task", command=self._callbacks["add_task"]).grid(
            row=1, column=2, padx=4, pady=16
        )
        tk.Button(controls, text="Edit Task", command=self._callbacks["edit_task"]).grid(
            row=1, column=3, padx=4, pady=16
        )
        tk.Button(controls, text="Delete Task", command=self._callbacks["delete_task"]).grid(
            row=1, column=4, padx=4, pady=16
        )
        self.phase_entry = phase_field.entry

        action_row = ButtonBar(self.body)
        action_row.pack(fill="x", pady=4)
        action_row.add("Submit Roadmap", self._callbacks["submit"])
        action_row.add("View Charts", self._callbacks["charts"])
        self.status_label = tk.Label(action_row, text="No roadmap")
        self.status_label.pack(side="right", padx=4)

        self.tree = ttk.Treeview(self.body, show="tree", height=10)
        self.tree.pack(fill="both", expand=True, pady=6)

    def set_student_choices(self, values: list[str]) -> None:
        self.student_select["values"] = values

    def set_team_choices(self, values: list[str]) -> None:
        self.team_select["values"] = values

    def selected_student(self) -> str:
        return self.student_select.get()

    def selected_team(self) -> str:
        return self.team_select.get()

    def set_invite_rows(self, rows: list[tuple]) -> None:
        for item in self.invite_table.get_children():
            self.invite_table.delete(item)
        for row in rows:
            self.invite_table.insert("", "end", values=row)

    def selected_invite_id(self) -> int | None:
        selection = self.invite_table.selection()
        if not selection:
            return None
        return int(self.invite_table.item(selection[0], "values")[0])

    def set_status(self, text: str) -> None:
        self.status_label.config(text=text)

    def clear_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

    def task_errors(self) -> list[str]:
        return self.task_form.validate()

    def task_data(self) -> dict:
        return self.task_form.get_data()

    def clear_task(self) -> None:
        self.task_form.clear()
