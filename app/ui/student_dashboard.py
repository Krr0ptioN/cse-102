from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.services.roadmap_service import (
    create_phase,
    create_roadmap,
    create_task,
    get_latest_roadmap,
    list_phases_with_tasks,
    submit_roadmap,
)
from app.services.team_service import list_all_teams
from app.services.validation import validate_roadmap


class StudentDashboard(tk.Frame):
    def __init__(self, master, db_path: str, on_back) -> None:
        super().__init__(master)
        self.db_path = db_path
        self.on_back = on_back
        self.current_team_id: int | None = None
        self.current_roadmap_id: int | None = None
        self.current_roadmap_status: str | None = None
        self._build()
        self._refresh_teams()

    def _build(self) -> None:
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)
        tk.Button(header, text="Back", command=self.on_back).pack(side="left", padx=10)
        tk.Label(header, text="Student Dashboard", font=("Helvetica", 16, "bold")).pack(
            side="left", padx=10
        )

        selector = tk.Frame(self)
        selector.pack(fill="x", pady=5)
        tk.Label(selector, text="Team").pack(side="left", padx=5)
        self.team_select = ttk.Combobox(selector, state="readonly")
        self.team_select.pack(side="left", padx=5)
        self.team_select.bind("<<ComboboxSelected>>", lambda _e: self._load_roadmap())

        content = tk.Frame(self)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_roadmap_panel(content)
        self._build_task_panel(content)

    def _build_roadmap_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Roadmap Builder")
        frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        controls = tk.Frame(frame)
        controls.pack(fill="x", padx=5, pady=5)

        self.phase_name_entry = tk.Entry(controls, width=20)
        self.phase_name_entry.grid(row=0, column=0, padx=5)
        tk.Button(controls, text="Add Phase", command=self._add_phase).grid(
            row=0, column=1, padx=5
        )

        self.task_title_entry = tk.Entry(controls, width=20)
        self.task_title_entry.grid(row=1, column=0, padx=5)
        self.task_weight_entry = tk.Entry(controls, width=8)
        self.task_weight_entry.grid(row=1, column=1, padx=5, sticky="w")
        tk.Button(controls, text="Add Task", command=self._add_task).grid(
            row=1, column=2, padx=5
        )

        tk.Button(controls, text="Submit Roadmap", command=self._submit_roadmap).grid(
            row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w"
        )

        self.roadmap_status_label = tk.Label(controls, text="No roadmap")
        self.roadmap_status_label.grid(row=2, column=2, padx=5)

        self.roadmap_tree = ttk.Treeview(frame, show="tree")
        self.roadmap_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def _build_task_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Tasks")
        frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.task_list = tk.Listbox(frame)
        self.task_list.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_text = tk.Text(frame, height=5)
        self.update_text.pack(fill="x", padx=5, pady=5)

        tk.Button(frame, text="Add Update").pack(pady=5)

    def _refresh_teams(self) -> None:
        teams = list_all_teams(self.db_path)
        self.team_choices = {f"{team['id']} {team['name']}": team["id"] for team in teams}
        self.team_select["values"] = list(self.team_choices.keys())
        if self.team_choices:
            self.team_select.current(0)
            self._load_roadmap()

    def _load_roadmap(self) -> None:
        selection = self.team_select.get()
        if not selection:
            return
        self.current_team_id = self.team_choices[selection]
        roadmap = get_latest_roadmap(self.db_path, self.current_team_id)
        if roadmap:
            self.current_roadmap_id = roadmap["id"]
            self.current_roadmap_status = roadmap["status"]
            self.roadmap_status_label.config(text=f"Status: {roadmap['status']}")
        else:
            self.current_roadmap_id = None
            self.current_roadmap_status = None
            self.roadmap_status_label.config(text="No roadmap")
        self._refresh_roadmap_tree()

    def _ensure_roadmap(self) -> int | None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return None
        if not self.current_roadmap_id:
            self.current_roadmap_id = create_roadmap(self.db_path, self.current_team_id)
            self.current_roadmap_status = "Draft"
            self.roadmap_status_label.config(text="Status: Draft")
        return self.current_roadmap_id

    def _add_phase(self) -> None:
        roadmap_id = self._ensure_roadmap()
        if not roadmap_id:
            return
        name = self.phase_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing data", "Enter a phase name.")
            return
        phases = list_phases_with_tasks(self.db_path, roadmap_id)
        sort_order = len(phases) + 1
        create_phase(self.db_path, roadmap_id, name, sort_order)
        self.phase_name_entry.delete(0, tk.END)
        self._refresh_roadmap_tree()

    def _add_task(self) -> None:
        roadmap_id = self._ensure_roadmap()
        if not roadmap_id:
            return
        title = self.task_title_entry.get().strip()
        weight_text = self.task_weight_entry.get().strip()
        if not title or not weight_text.isdigit():
            messagebox.showwarning("Missing data", "Enter a task title and numeric weight.")
            return
        phase_id = self._selected_phase_id()
        if not phase_id:
            messagebox.showwarning("No phase", "Select a phase in the roadmap tree.")
            return
        create_task(self.db_path, phase_id, title, int(weight_text))
        self.task_title_entry.delete(0, tk.END)
        self.task_weight_entry.delete(0, tk.END)
        self._refresh_roadmap_tree()

    def _submit_roadmap(self) -> None:
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        if self.current_roadmap_status != "Draft":
            messagebox.showwarning("Locked", "Roadmap is already submitted or approved.")
            return
        phases = list_phases_with_tasks(self.db_path, self.current_roadmap_id)
        payload = [{"tasks": [task["weight"] for task in p["tasks"]]} for p in phases]
        result = validate_roadmap(payload)
        if not result["ok"]:
            messagebox.showwarning("Invalid roadmap", result["reason"])
            return
        if result.get("weight_warning"):
            proceed = messagebox.askyesno(
                "Weight warning", "Weights do not sum to 100. Submit anyway?"
            )
            if not proceed:
                return
        submit_roadmap(self.db_path, self.current_roadmap_id)
        self.current_roadmap_status = "Submitted"
        self.roadmap_status_label.config(text="Status: Submitted")

    def _refresh_roadmap_tree(self) -> None:
        for row in self.roadmap_tree.get_children():
            self.roadmap_tree.delete(row)
        if not self.current_roadmap_id:
            return
        phases = list_phases_with_tasks(self.db_path, self.current_roadmap_id)
        for phase in phases:
            phase_id = phase["id"]
            phase_item = self.roadmap_tree.insert(
                "", "end", iid=f"phase-{phase_id}", text=f"Phase: {phase['name']}"
            )
            for task in phase["tasks"]:
                self.roadmap_tree.insert(
                    phase_item,
                    "end",
                    iid=f"task-{task['id']}",
                    text=f"Task: {task['title']} (w{task['weight']})",
                )

    def _selected_phase_id(self) -> int | None:
        selection = self.roadmap_tree.selection()
        if not selection:
            return None
        item_id = selection[0]
        if item_id.startswith("phase-"):
            return int(item_id.split("-", 1)[1])
        if item_id.startswith("task-"):
            parent = self.roadmap_tree.parent(item_id)
            if parent.startswith("phase-"):
                return int(parent.split("-", 1)[1])
        return None
