from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService
from app.services.validation import validate_roadmap
from app.ui.charts import show_charts_window
from app.ui.components import AppShell, DataTable, DetailsDrawer, Modal, Section, StatCard


class StudentDashboard(tk.Frame):
    def __init__(
        self,
        master,
        team_service: TeamService,
        roadmap_service: RoadmapService,
        task_service: TaskService,
        on_back,
    ) -> None:
        super().__init__(master)
        self.on_back = on_back
        self.current_team_id: int | None = None
        self.current_roadmap_id: int | None = None
        self.current_roadmap_status: str | None = None
        self.team_service = team_service
        self.roadmap_service = roadmap_service
        self.task_service = task_service

        self.shell = AppShell(self, "Student Workspace", on_back)
        self.shell.pack(fill="both", expand=True)

        self._build_layout()
        self._refresh_teams()

    def _build_layout(self) -> None:
        content = self.shell.content
        content.grid_rowconfigure(1, weight=1)
        content.grid_rowconfigure(2, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_columnconfigure(2, weight=0, minsize=260)

        self.stats_row = tk.Frame(content)
        self.stats_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=8)
        self.stats_row.grid_columnconfigure((0, 1), weight=1)

        self.stat_status = StatCard(self.stats_row, "Roadmap Status", "-")
        self.stat_status.grid(row=0, column=0, padx=8, sticky="ew")
        self.stat_done = StatCard(self.stats_row, "Tasks Done", "0")
        self.stat_done.grid(row=0, column=1, padx=8, sticky="ew")

        self.roadmap_section = Section(content, "Roadmap Builder")
        self.roadmap_section.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self._build_roadmap_panel(self.roadmap_section.body)

        self.task_section = Section(content, "Tasks")
        self.task_section.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self._build_task_panel(self.task_section.body)

        self.comments_section = Section(content, "Roadmap Comments")
        self.comments_section.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)
        self._build_comments_panel(self.comments_section.body)

        self.drawer = DetailsDrawer(content, "Details")
        self.drawer.grid(row=1, column=2, sticky="nsew", padx=8, pady=8)

    def _build_roadmap_panel(self, parent: tk.Frame) -> None:
        selector = tk.Frame(parent)
        selector.pack(fill="x", pady=4)
        tk.Label(selector, text="Team").pack(side="left", padx=4)
        self.team_select = ttk.Combobox(selector, state="readonly")
        self.team_select.pack(side="left", padx=4)
        self.team_select.bind("<<ComboboxSelected>>", lambda _e: self._load_roadmap())

        controls = tk.Frame(parent)
        controls.pack(fill="x", pady=6)

        self.phase_name_entry = tk.Entry(controls, width=20)
        self.phase_name_entry.grid(row=0, column=0, padx=4)
        tk.Button(controls, text="Add Phase", command=self._add_phase).grid(
            row=0, column=1, padx=4
        )
        tk.Button(controls, text="Edit Phase", command=self._edit_phase).grid(
            row=0, column=2, padx=4
        )
        tk.Button(controls, text="Delete Phase", command=self._delete_phase).grid(
            row=0, column=3, padx=4
        )

        self.task_title_entry = tk.Entry(controls, width=20)
        self.task_title_entry.grid(row=1, column=0, padx=4)
        self.task_weight_entry = tk.Entry(controls, width=8)
        self.task_weight_entry.grid(row=1, column=1, padx=4, sticky="w")
        tk.Button(controls, text="Add Task", command=self._add_task).grid(
            row=1, column=2, padx=4
        )
        tk.Button(controls, text="Edit Task", command=self._edit_task).grid(
            row=1, column=3, padx=4
        )
        tk.Button(controls, text="Delete Task", command=self._delete_task).grid(
            row=1, column=4, padx=4
        )

        action_row = tk.Frame(parent)
        action_row.pack(fill="x", pady=4)
        tk.Button(action_row, text="Submit Roadmap", command=self._submit_roadmap).pack(
            side="left", padx=4
        )
        tk.Button(action_row, text="View Charts", command=self._show_charts).pack(
            side="left", padx=4
        )
        self.roadmap_status_label = tk.Label(action_row, text="No roadmap")
        self.roadmap_status_label.pack(side="right", padx=4)

        self.roadmap_tree = ttk.Treeview(parent, show="tree", height=10)
        self.roadmap_tree.pack(fill="both", expand=True, pady=6)

    def _build_task_panel(self, parent: tk.Frame) -> None:
        self.task_table = DataTable(parent, ["Id", "Task", "Status", "Weight"], height=7)
        self.task_table.pack(fill="both", expand=True, pady=6)
        self.task_table.bind("<<TreeviewSelect>>", lambda _e: self._refresh_updates())

        actions = tk.Frame(parent)
        actions.pack(fill="x", pady=4)
        tk.Button(actions, text="In Progress", command=lambda: self._set_task_status("In Progress")).pack(
            side="left", padx=4
        )
        tk.Button(actions, text="Done", command=lambda: self._set_task_status("Done")).pack(
            side="left", padx=4
        )

        member_row = tk.Frame(parent)
        member_row.pack(fill="x", pady=4)
        tk.Label(member_row, text="Update as").pack(side="left", padx=4)
        self.member_select = ttk.Combobox(member_row, state="readonly")
        self.member_select.pack(side="left", padx=4)

        self.update_text = tk.Text(parent, height=4)
        self.update_text.pack(fill="x", pady=6)
        tk.Button(parent, text="Add Update", command=self._add_update).pack(anchor="e")

        self.update_table = DataTable(parent, ["User", "Update", "Time"], height=6)
        self.update_table.pack(fill="both", expand=True, pady=6)

    def _build_comments_panel(self, parent: tk.Frame) -> None:
        action = tk.Frame(parent)
        action.pack(fill="x", pady=4)
        tk.Button(action, text="Add Comment", command=self._add_comment).pack(
            side="left", padx=4
        )

        self.comment_table = DataTable(parent, ["Author", "Comment", "Time"], height=5)
        self.comment_table.pack(fill="both", expand=True, pady=6)

    def _refresh_teams(self) -> None:
        teams = self.team_service.list_all_teams()
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
        roadmap = self.roadmap_service.get_latest_roadmap(self.current_team_id)
        if roadmap:
            self.current_roadmap_id = roadmap["id"]
            self.current_roadmap_status = roadmap["status"]
            self.roadmap_status_label.config(text=f"Status: {roadmap['status']}")
        else:
            self.current_roadmap_id = None
            self.current_roadmap_status = None
            self.roadmap_status_label.config(text="No roadmap")
        self._refresh_team_members()
        self._refresh_roadmap_tree()
        self._refresh_task_list()
        self._refresh_comments()
        self._refresh_stats()

    def _ensure_roadmap(self) -> int | None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return None
        if not self.current_roadmap_id:
            self.current_roadmap_id = self.roadmap_service.create_roadmap(self.current_team_id)
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
        phases = self.roadmap_service.list_phases_with_tasks(roadmap_id)
        sort_order = len(phases) + 1
        self.roadmap_service.create_phase(roadmap_id, name, sort_order)
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
        self.roadmap_service.create_task(phase_id, title, int(weight_text))
        self.task_title_entry.delete(0, tk.END)
        self.task_weight_entry.delete(0, tk.END)
        self._refresh_roadmap_tree()
        self._refresh_task_list()
        self._refresh_stats()

    def _submit_roadmap(self) -> None:
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        if self.current_roadmap_status != "Draft":
            messagebox.showwarning("Locked", "Roadmap is already submitted or approved.")
            return
        phases = self.roadmap_service.list_phases_with_tasks(self.current_roadmap_id)
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
        self.roadmap_service.submit_roadmap(self.current_roadmap_id)
        self.current_roadmap_status = "Submitted"
        self.roadmap_status_label.config(text="Status: Submitted")
        self._refresh_stats()

    def _refresh_roadmap_tree(self) -> None:
        for row in self.roadmap_tree.get_children():
            self.roadmap_tree.delete(row)
        if not self.current_roadmap_id:
            return
        phases = self.roadmap_service.list_phases_with_tasks(self.current_roadmap_id)
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

    def _refresh_task_list(self) -> None:
        if not self.current_roadmap_id:
            self.task_table.set_rows([])
            return
        self.tasks_cache = self.task_service.list_tasks_for_roadmap(self.current_roadmap_id)
        rows = [(t["id"], t["title"], t["status"], t["weight"]) for t in self.tasks_cache]
        self.task_table.set_rows(rows)
        self._refresh_stats()

    def _refresh_comments(self) -> None:
        if not self.current_roadmap_id:
            self.comment_table.set_rows([])
            return
        comments = self.roadmap_service.list_roadmap_comments(self.current_roadmap_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        self.comment_table.set_rows(rows)

    def _set_task_status(self, status: str) -> None:
        if self.current_roadmap_status != "Approved":
            messagebox.showwarning("Not approved", "Roadmap is not approved yet.")
            return
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showwarning("No task", "Select a task first.")
            return
        self.task_service.update_task_status(task_id, status)
        self._refresh_task_list()

    def _add_update(self) -> None:
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showwarning("No task", "Select a task first.")
            return
        selection = self.member_select.get()
        if not selection:
            messagebox.showwarning("No member", "Select a member for this update.")
            return
        text = self.update_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("Missing data", "Enter an update note.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.task_service.add_update(task_id, user_id, text)
        self.update_text.delete("1.0", tk.END)
        self._refresh_updates()

    def _add_comment(self) -> None:
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        selection = self.member_select.get()
        if not selection:
            messagebox.showwarning("No member", "Select a member for this comment.")
            return
        user_name = selection.split(" ", 1)[1]
        modal = Modal(self, "Add Comment")
        tk.Label(modal.body, text="Comment").pack(anchor="w")
        note = tk.Text(modal.body, height=4, width=40)
        note.pack(fill="x", pady=6)

        def save() -> None:
            text = note.get("1.0", tk.END).strip()
            if not text:
                messagebox.showwarning("Missing data", "Enter a comment.")
                return
            self.roadmap_service.add_roadmap_comment(self.current_roadmap_id, user_name, text, "comment")
            modal.destroy()
            self._refresh_comments()

        modal.bind("<Escape>", lambda _e: modal.destroy())
        modal.bind("<Return>", lambda _e: save())
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _refresh_updates(self) -> None:
        task_id = self._selected_task_id()
        if not task_id:
            self.update_table.set_rows([])
            return
        updates = self.task_service.list_updates_for_task(task_id)
        rows = [(u["user"], u["text"], u["created_at"]) for u in updates]
        self.update_table.set_rows(rows)
        self._show_task_details(task_id, updates)

    def _refresh_team_members(self) -> None:
        if not self.current_team_id:
            return
        members = self.team_service.list_team_members(self.current_team_id)
        choices = [f"{m['id']} {m['name']}" for m in members]
        self.member_select["values"] = choices
        if choices:
            self.member_select.current(0)

    def _refresh_stats(self) -> None:
        status = self.current_roadmap_status or "-"
        self.stat_status.set_value(status)
        done = len([t for t in getattr(self, "tasks_cache", []) if t["status"] == "Done"])
        self.stat_done.set_value(str(done))

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

    def _selected_task_id(self) -> int | None:
        selection = self.task_table.selection()
        if not selection:
            return None
        return int(self.task_table.item(selection[0], "values")[0])

    def _show_task_details(self, task_id: int, updates: list[dict]) -> None:
        row = None
        for task in getattr(self, "tasks_cache", []):
            if task["id"] == task_id:
                row = task
                break
        if not row:
            return
        self.drawer.clear()
        tk.Label(self.drawer.body, text=f"Task #{row['id']}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Title: {row['title']}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Status: {row['status']}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Weight: {row['weight']}").pack(anchor="w")
        tk.Label(
            self.drawer.body, text="Recent Updates", font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(10, 4))
        if not updates:
            tk.Label(self.drawer.body, text="No updates yet").pack(anchor="w")
            return
        for upd in updates[:5]:
            row = tk.Frame(self.drawer.body)
            row.pack(fill="x", pady=2)
            tk.Label(row, text="●", fg="#0f766e").pack(side="left")
            tk.Label(
                row, text=f"{upd['user']}: {upd['text']}", wraplength=200, justify="left"
            ).pack(side="left", padx=6)
            tk.Label(row, text=upd["created_at"], fg="#5f6b68").pack(side="right")

    def _edit_phase(self) -> None:
        phase_id = self._selected_phase_id()
        if not phase_id:
            messagebox.showwarning("No phase", "Select a phase first.")
            return
        modal = Modal(self, "Edit Phase")
        tk.Label(modal.body, text="Phase Name").grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(modal.body, width=24)
        name_entry.grid(row=0, column=1, padx=6, pady=4)
        current = self.roadmap_tree.item(f"phase-{phase_id}", "text").replace("Phase: ", "")
        name_entry.insert(0, current)

        def save() -> None:
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing data", "Enter a phase name.")
                return
            self.roadmap_service.update_phase(phase_id, name)
            modal.destroy()
            self._refresh_roadmap_tree()

        modal.bind("<Escape>", lambda _e: modal.destroy())
        modal.bind("<Return>", lambda _e: save())
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _delete_phase(self) -> None:
        phase_id = self._selected_phase_id()
        if not phase_id:
            messagebox.showwarning("No phase", "Select a phase first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this phase and its tasks?"):
            return
        self.roadmap_service.delete_phase(phase_id)
        self._refresh_roadmap_tree()
        self._refresh_task_list()

    def _edit_task(self) -> None:
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showwarning("No task", "Select a task first.")
            return
        row = self.task_table.item(self.task_table.selection()[0], "values")
        modal = Modal(self, "Edit Task")
        tk.Label(modal.body, text="Title").grid(row=0, column=0, sticky="w")
        tk.Label(modal.body, text="Weight").grid(row=1, column=0, sticky="w")
        title_entry = tk.Entry(modal.body, width=24)
        weight_entry = tk.Entry(modal.body, width=10)
        title_entry.grid(row=0, column=1, padx=6, pady=4)
        weight_entry.grid(row=1, column=1, padx=6, pady=4)
        title_entry.insert(0, row[1])
        weight_entry.insert(0, row[3])

        def save() -> None:
            title = title_entry.get().strip()
            weight_text = weight_entry.get().strip()
            if not title or not weight_text.isdigit():
                messagebox.showwarning("Missing data", "Enter title and numeric weight.")
                return
            self.roadmap_service.update_task_details(task_id, title, int(weight_text))
            modal.destroy()
            self._refresh_roadmap_tree()
            self._refresh_task_list()

        modal.bind("<Escape>", lambda _e: modal.destroy())
        modal.bind("<Return>", lambda _e: save())
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _delete_task(self) -> None:
        task_id = self._selected_task_id()
        if not task_id:
            messagebox.showwarning("No task", "Select a task first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this task?"):
            return
        self.roadmap_service.delete_task(task_id)
        self._refresh_roadmap_tree()
        self._refresh_task_list()

    def _show_charts(self) -> None:
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        tasks = self.task_service.list_tasks_for_roadmap(self.current_roadmap_id)
        show_charts_window(self, "Team Charts", tasks)
