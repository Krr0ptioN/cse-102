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
    tk_style,
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
        tk.Label(invite_block, text="Invitations").pack(anchor="w")
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
        selector.pack(fill="x", pady=4)
        team_field = LabeledCombobox(selector, "Team", width=34)
        team_field.pack(side="left", padx=4)
        self.team_select = team_field.combo
        self.team_select.bind(
            "<<ComboboxSelected>>", lambda _e: self._callbacks["team_change"]()
        )

        team_actions = ButtonBar(self.body)
        team_actions.pack(fill="x", pady=(0, 6))
        team_actions.add("Create Team", self._callbacks["create_team"])
        team_actions.add("Invite Student", self._callbacks["invite_student"])

        controls = tk.Frame(self.body)
        controls.pack(fill="x", pady=6)

        phase_field = LabeledEntry(controls, "Phase Name", width=20)
        phase_field.grid(row=0, column=0, padx=4, sticky="w")
        Button(controls,variant="danger", text="Add Phase", command=self._callbacks["add_phase"]).grid(
            row=0, column=1, padx=4, pady=16
        )
        Button(controls, text="Edit Phase", command=self._callbacks["edit_phase"]).grid(
            row=0, column=2, padx=4, pady=16
        )
        Button(
            controls, text="Delete Phase", command=self._callbacks["delete_phase"]
        ).grid(row=0, column=3, padx=4, pady=16)

        self.task_form.render(controls, columns=2, start_row=1)
        Button(controls, text="Add Task", command=self._callbacks["add_task"]).grid(
            row=1, column=2, padx=4, pady=16
        )
        Button(controls, text="Edit Task", command=self._callbacks["edit_task"]).grid(
            row=1, column=3, padx=4, pady=16
        )
        Button(
            controls, text="Delete Task", command=self._callbacks["delete_task"]
        ).grid(row=1, column=4, padx=4, pady=16)
        self.phase_entry = phase_field.entry

        action_row = ButtonBar(self.body)
        action_row.pack(fill="x", pady=4)
        action_row.add("Submit Roadmap", self._callbacks["submit"])
        action_row.add("View Charts", self._callbacks["charts"])
        self.status_label = tk.Label(action_row, text="No roadmap")
        self.status_label.pack(side="right", padx=4)

        tree_card = Card(self.body)
        tree_card.pack(fill="both", expand=True, pady=6)

        tree_toolbar = tk.Frame(tree_card, bg=tree_card["bg"])
        tree_toolbar.pack(fill="x", padx=10, pady=(10, 6))
        tk.Label(tree_toolbar, text="Roadmap Outline", bg=tree_card["bg"]).pack(
            side="left"
        )

        self.tree_filter = Input(
            tree_toolbar,
            width=28,
            textvariable=self._tree_filter_var,
        )
        self.tree_filter.pack(side="right", padx=(8, 0))
        self.tree_filter.bind("<KeyRelease>", lambda _e: self._apply_tree_filter())
        Button(
            tree_toolbar,
            text="Clear",
            size="sm",
            variant="secondary",
            command=self._clear_tree_filter,
        ).pack(side="right")

        tree_container = tk.Frame(tree_card, bg=tree_card["bg"])
        tree_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        tk_style(tree_container)
        self.tree = ttk.Treeview(
            tree_container,
            show="tree",
            height=10,
            style="Ds.Treeview",
        )
        tree_scroll = ttk.Scrollbar(
            tree_container,
            orient="vertical",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

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
        for item in self.tree.get_children():
            self.tree.delete(item)

    def _apply_tree_filter(self) -> None:
        self._render_tree()

    def _clear_tree_filter(self) -> None:
        self._tree_filter_var.set("")
        self._render_tree()

    def _render_tree(self) -> None:
        for item in self.tree.get_children():
            self.tree.delete(item)

        query = self._tree_filter_var.get().strip().lower()
        for phase in self._tree_phases:
            phase_name = str(phase.get("name", ""))
            phase_matches = not query or query in phase_name.lower()
            tasks = phase.get("tasks", [])

            if phase_matches:
                visible_tasks = tasks
            else:
                visible_tasks = [
                    task
                    for task in tasks
                    if query in str(task.get("title", "")).lower()
                ]

            if not phase_matches and not visible_tasks:
                continue

            phase_id = phase["id"]
            phase_item = self.tree.insert(
                "",
                "end",
                iid=f"phase-{phase_id}",
                text=f"Phase: {phase_name}",
            )

            for task in visible_tasks:
                self.tree.insert(
                    phase_item,
                    "end",
                    iid=f"task-{task['id']}",
                    text=f"Task: {task['title']} (w{task['weight']})",
                )

            self.tree.item(phase_item, open=True)

    def task_errors(self) -> list[str]:
        return self.task_form.validate()

    def task_data(self) -> dict:
        return self.task_form.get_data()

    def clear_task(self) -> None:
        self.task_form.clear()
