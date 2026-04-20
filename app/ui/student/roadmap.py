from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from libs.ui_kit import (
    Button,
    ButtonBar,
    Card,
    DataTable,
    Input,
    LabeledCombobox,
    LabeledEntry,
    Section,
    PhaseListView,
    palette
)
from ui.student.forms import TaskForm


class RoadmapBuilderSection(Section):
    def __init__(
        self,
        master,
        on_student_change,
        on_invite_accept,
        on_invite_decline,
        on_create_team,
        on_invite_student,
        on_team_change,
        on_add_phase,
        on_edit_phase,
        on_delete_phase,
        on_add_task,
        on_edit_task,
        on_delete_task,
        on_submit,
        on_charts,
        show_student_selector: bool = True,
    ) -> None:
        super().__init__(master, "Roadmap Builder")
        self.show_student_selector = show_student_selector
        self.student_select: ttk.Combobox | None = None
        self._callbacks = {
            "student_change": on_student_change,
            "invite_accept": on_invite_accept,
            "invite_decline": on_invite_decline,
            "create_team": on_create_team,
            "invite_student": on_invite_student,
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
        self._tree_phases: list[dict] = []
        self._tree_filter_var = tk.StringVar(value="")
        self._build()

    def _build(self) -> None:
        if self.show_student_selector:
            student_row = tk.Frame(self.body)
            student_row.pack(fill="x", pady=4)
            student_field = LabeledCombobox(student_row, "Student", width=28)
            student_field.pack(side="left", padx=4)
            self.student_select = student_field.combo
            self.student_select.bind(
                "<<ComboboxSelected>>", lambda _e: self._callbacks["student_change"]()
            )

        invite_block = tk.Frame(self.body)
        invite_block.pack(fill="x", pady=4)
        tk.Label(invite_block, text="Invitations", font=("TkDefaultFont", 10, "bold")).pack(anchor="w")
        self.invite_table = DataTable(
            invite_block,
            ["Id", "Team", "Status"],
            height=3,
        )
        self.invite_table.pack(fill="x", pady=4)
        invite_actions = ButtonBar(invite_block)
        invite_actions.pack(fill="x")
        invite_actions.add("Accept", self._callbacks["invite_accept"])
        invite_actions.add("Decline", self._callbacks["invite_decline"])

        selector = tk.Frame(self.body)
        selector.pack(fill="x", pady=12)
        team_field = LabeledCombobox(selector, "Active Team Context", width=42)
        team_field.pack(side="left", padx=4)
        self.team_select = team_field.combo
        self.team_select.bind(
            "<<ComboboxSelected>>", lambda _e: self._callbacks["team_change"]()
        )

        team_actions = ButtonBar(self.body)
        team_actions.pack(fill="x", pady=(0, 12))
        team_actions.add("Create Team", self._callbacks["create_team"])
        team_actions.add("Invite Student", self._callbacks["invite_student"])

        controls = Card(self.body)
        controls.pack(fill="x", pady=6)
        
        inner_ctrl = tk.Frame(controls, bg=controls["bg"], padx=12, pady=12)
        inner_ctrl.pack(fill="x")

        phase_field = LabeledEntry(inner_ctrl, "Phase Name", width=20)
        phase_field.grid(row=0, column=0, padx=4, sticky="w")
        Button(inner_ctrl, text="Add Phase", variant="secondary", size="sm", command=self._callbacks["add_phase"]).grid(
            row=0, column=1, padx=4, sticky="ew"
        )
        
        self.task_form.render(inner_ctrl, columns=2, start_row=1)
        Button(inner_ctrl, text="Add Task to Phase", size="sm", command=self._callbacks["add_task"]).grid(
            row=1, column=2, padx=4, sticky="ew"
        )
        self.phase_entry = phase_field.entry

        action_row = ButtonBar(self.body)
        action_row.pack(fill="x", pady=12)
        action_row.add("Submit Roadmap for Review", self._callbacks["submit"])
        
        self.status_label = tk.Label(action_row, text="No roadmap", font=("TkDefaultFont", 10, "bold"))
        self.status_label.pack(side="right", padx=12)

        outline_label = tk.Label(self.body, text="Roadmap Outline", font=("TkDefaultFont", 12, "bold"))
        outline_label.pack(anchor="w", padx=4, pady=(12, 4))

        self.phase_list = PhaseListView(
            self.body, 
            on_task_select=self._callbacks["edit_task"],
            on_edit_phase=self._callbacks["edit_phase"],
            on_delete_phase=self._callbacks["delete_phase"]
        )
        self.phase_list.pack(fill="both", expand=True, pady=4)

    def set_student_choices(self, values: list[str]) -> None:
        if self.student_select is not None:
            self.student_select["values"] = values

    def set_team_choices(self, values: list[str]) -> None:
        self.team_select["values"] = values

    def selected_student(self) -> str:
        return self.student_select.get() if self.student_select is not None else ""

    def selected_team(self) -> str:
        return self.team_select.get()

    def set_invite_rows(self, rows: list[tuple]) -> None:
        self.invite_table.set_rows(rows)

    def selected_invite_id(self) -> int | None:
        selection = self.invite_table.selection()
        if not selection:
            return None
        return int(self.invite_table.item(selection[0], "values")[0])

    def set_status(self, text: str) -> None:
        self.status_label.config(text=text)

    def set_roadmap_tree(self, phases: list[dict]) -> None:
        self._tree_phases = list(phases)
        self._render_tree()

    def clear_tree(self) -> None:
        self._tree_phases = []
        self.phase_list.set_phases([])

    def _render_tree(self) -> None:
        self.phase_list.set_phases(self._tree_phases)

    def task_errors(self) -> list[str]:
        return self.task_form.validate()

    def task_data(self) -> dict:
        return self.task_form.get_data()

    def clear_task(self) -> None:
        self.task_form.clear()
