from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox, ttk

from app.services.checkin import CheckinService
from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService
from app.services.classes import ClassService
from app.services.validation import validate_roadmap
from app.ui.charts import show_charts_window
from app.ui.components import Modal, bind_modal_keys
from app.ui.dashboard_base import DashboardBase
from app.ui.forms import CommentForm, TaskForm
from app.ui.student import (
    RoadmapBuilderSection,
    StudentCheckinsSection,
    StudentCommentsSection,
    StudentStatsRow,
    TaskSection,
)


class StudentDashboard(DashboardBase):
    def __init__(
        self,
        master,
        class_service: ClassService,
        checkin_service: CheckinService,
        team_service: TeamService,
        roadmap_service: RoadmapService,
        task_service: TaskService,
        on_back,
    ) -> None:
        self.current_team_id: int | None = None
        self.current_roadmap_id: int | None = None
        self.current_roadmap_status: str | None = None
        self.active_student_id: int | None = None
        self.class_service = class_service
        self.checkin_service = checkin_service
        self.team_service = team_service
        self.roadmap_service = roadmap_service
        self.task_service = task_service

        super().__init__(master, "Student Workspace", on_back)

        self._refresh_students()

    def build_layout(self) -> None:
        content = self.shell.content
        self.configure_content_grid((1, 1, 0))

        self.stats_row = StudentStatsRow(content)
        self.stats_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=8)

        self.roadmap_section = RoadmapBuilderSection(
            content,
            self._set_active_student,
            self._accept_invite,
            self._decline_invite,
            self._load_roadmap,
            self._add_phase,
            self._edit_phase,
            self._delete_phase,
            self._add_task,
            self._edit_task,
            self._delete_task,
            self._submit_roadmap,
            self._show_charts,
        )
        self.roadmap_section.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)

        self.task_section = TaskSection(
            content, self._refresh_updates, self._set_task_status, self._add_update
        )
        self.task_section.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)

        bottom_tabs = ttk.Notebook(content)
        bottom_tabs.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=8, pady=8)

        self.comments_section = StudentCommentsSection(bottom_tabs, self._add_comment)
        bottom_tabs.add(self.comments_section, text="Comments")

        self.checkins_section = StudentCheckinsSection(
            bottom_tabs, self._submit_checkin
        )
        bottom_tabs.add(self.checkins_section, text="Check-ins")

        self.mount_drawer(row=1, column=2)

    def _refresh_teams(self) -> None:
        teams = (
            self.team_service.list_teams_for_user(self.active_student_id)
            if self.active_student_id
            else []
        )
        self.team_choices = {}
        for team in teams:
            principal = team.get("principal_name") or "Unassigned"
            label = f"{team['id']} {team['name']} · Principal: {principal}"
            self.team_choices[label] = team["id"]
        self.roadmap_section.set_team_choices(list(self.team_choices.keys()))
        if self.team_choices:
            self.roadmap_section.team_select.current(0)
            self._load_roadmap()
        else:
            self.current_team_id = None
            self.current_roadmap_id = None
            self.roadmap_section.set_status("No roadmap")
            self.task_section.set_task_rows([])
            self.comments_section.set_comment_rows([])
            self.task_section.set_update_rows([])
            self.roadmap_section.clear_tree()
            self.checkins_section.set_rows([])
            self.checkins_section.set_progress(0, 0, 0)

    def _refresh_students(self) -> None:
        students = self.class_service.list_users(role="student")
        choices = [f"{s['id']} {s['name']}" for s in students]
        self.roadmap_section.set_student_choices(choices)
        if not choices:
            self.active_student_id = None
            self.roadmap_section.set_invite_rows([])
            self.roadmap_section.set_team_choices([])
            return
        if not self.roadmap_section.selected_student():
            self.roadmap_section.student_select.current(0)
            self._set_active_student()

    def _set_active_student(self) -> None:
        selection = self.roadmap_section.selected_student()
        if not selection:
            return
        self.active_student_id = int(selection.split(" ", 1)[0])
        self._refresh_invitations()
        self._refresh_teams()

    def _refresh_invitations(self) -> None:
        if not self.active_student_id:
            self.roadmap_section.set_invite_rows([])
            return
        invites = self.team_service.list_invitations_for_user(self.active_student_id)
        rows = [(i["id"], i["team"], i["status"]) for i in invites]
        self.roadmap_section.set_invite_rows(rows)

    def _accept_invite(self) -> None:
        invite_id = self.roadmap_section.selected_invite_id()
        if not invite_id:
            messagebox.showwarning("No invite", "Select an invite to accept.")
            return
        self.team_service.accept_invitation(invite_id)
        self._refresh_invitations()
        self._refresh_teams()

    def _decline_invite(self) -> None:
        invite_id = self.roadmap_section.selected_invite_id()
        if not invite_id:
            messagebox.showwarning("No invite", "Select an invite to decline.")
            return
        self.team_service.decline_invitation(invite_id)
        self._refresh_invitations()

    def _load_roadmap(self) -> None:
        selection = self.roadmap_section.selected_team()
        if not selection:
            return
        self.current_team_id = self.team_choices[selection]
        self._show_team_details()
        roadmap = self.roadmap_service.get_latest_roadmap(self.current_team_id)
        if roadmap:
            self.current_roadmap_id = roadmap["id"]
            self.current_roadmap_status = roadmap["status"]
            self.roadmap_section.set_status(f"Status: {roadmap['status']}")
        else:
            self.current_roadmap_id = None
            self.current_roadmap_status = None
            self.roadmap_section.set_status("No roadmap")
        self._refresh_team_members()
        self._refresh_roadmap_tree()
        self._refresh_task_list()
        self._refresh_comments()
        self._refresh_checkins()
        self._refresh_stats()

    def _show_team_details(self) -> None:
        if not self.current_team_id:
            return
        team = self.team_service.get_team(self.current_team_id)
        if not team:
            return
        self.drawer.clear()
        self._render_team_header(team)

    def _render_team_header(self, team: dict) -> None:
        principal = team.get("principal_name") or "Unassigned"
        self.drawer.render_team_header(team["id"], team["name"], principal)

    def _ensure_roadmap(self) -> int | None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return None
        if not self.current_roadmap_id:
            self.current_roadmap_id = self.roadmap_service.create_roadmap(
                self.current_team_id
            )
            self.current_roadmap_status = "Draft"
            self.roadmap_section.set_status("Status: Draft")
        return self.current_roadmap_id

    def _add_phase(self) -> None:
        roadmap_id = self._ensure_roadmap()
        if not roadmap_id:
            return
        name = self.roadmap_section.phase_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing data", "Enter a phase name.")
            return
        phases = self.roadmap_service.list_phases_with_tasks(roadmap_id)
        sort_order = len(phases) + 1
        self.roadmap_service.create_phase(roadmap_id, name, sort_order)
        self.roadmap_section.phase_entry.delete(0, tk.END)
        self._refresh_roadmap_tree()

    def _add_task(self) -> None:
        roadmap_id = self._ensure_roadmap()
        if not roadmap_id:
            return
        errors = self.roadmap_section.task_errors()
        if errors:
            messagebox.showwarning("Invalid data", "\n".join(errors))
            return
        data = self.roadmap_section.task_data()
        title = data["title"]
        weight_text = data["weight"]
        phase_id = self._selected_phase_id()
        if not phase_id:
            messagebox.showwarning("No phase", "Select a phase in the roadmap tree.")
            return
        self.roadmap_service.create_task(phase_id, title, int(weight_text))
        self.roadmap_section.clear_task()
        self._refresh_roadmap_tree()
        self._refresh_task_list()
        self._refresh_stats()

    def _submit_roadmap(self) -> None:
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        if self.current_roadmap_status != "Draft":
            messagebox.showwarning(
                "Locked", "Roadmap is already submitted or approved."
            )
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
        self.roadmap_section.set_status("Status: Submitted")
        self._refresh_stats()

    def _refresh_roadmap_tree(self) -> None:
        for row in self.roadmap_section.tree.get_children():
            self.roadmap_section.tree.delete(row)
        if not self.current_roadmap_id:
            return
        phases = self.roadmap_service.list_phases_with_tasks(self.current_roadmap_id)
        for phase in phases:
            phase_id = phase["id"]
            phase_item = self.roadmap_section.tree.insert(
                "", "end", iid=f"phase-{phase_id}", text=f"Phase: {phase['name']}"
            )
            for task in phase["tasks"]:
                self.roadmap_section.tree.insert(
                    phase_item,
                    "end",
                    iid=f"task-{task['id']}",
                    text=f"Task: {task['title']} (w{task['weight']})",
                )

    def _refresh_task_list(self) -> None:
        if not self.current_roadmap_id:
            self.task_section.set_task_rows([])
            return
        self.tasks_cache = self.task_service.list_tasks_for_roadmap(
            self.current_roadmap_id
        )
        rows = [
            (t["id"], t["title"], t["status"], t["weight"]) for t in self.tasks_cache
        ]
        self.task_section.set_task_rows(rows)
        self._refresh_progress()
        self._refresh_stats()

    def _refresh_comments(self) -> None:
        if not self.current_roadmap_id:
            self.comments_section.set_comment_rows([])
            return
        comments = self.roadmap_service.list_roadmap_comments(self.current_roadmap_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        self.comments_section.set_comment_rows(rows)

    def _refresh_checkins(self) -> None:
        if not self.current_team_id:
            self.checkins_section.set_rows([])
            return
        checkins = self.checkin_service.list_checkins_for_team(self.current_team_id)
        rows = [
            (
                c["id"],
                f"{c['week_start']} → {c['week_end']}",
                c["status"],
                f"{c['percent']}%",
                c["submitted_at"],
            )
            for c in checkins
        ]
        self.checkins_section.set_rows(rows)

    def _refresh_progress(self) -> None:
        if not self.current_team_id:
            self.checkins_section.set_progress(0, 0, 0)
            return
        metrics = self.checkin_service.compute_metrics(self.current_team_id)
        self.checkins_section.set_progress(
            metrics["percent"], metrics["done"], metrics["total"]
        )

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
        selection = self.task_section.selected_member_label()
        if not selection:
            messagebox.showwarning("No member", "Select a member for this update.")
            return
        text = self.task_section.get_update_text()
        if not text:
            messagebox.showwarning("Missing data", "Enter an update note.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.task_service.add_update(task_id, user_id, text)
        self.task_section.clear_update_text()
        self._refresh_updates()

    def _current_week_range(self) -> tuple[str, str]:
        today = date.today()
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start.isoformat(), end.isoformat()

    def _submit_checkin(self) -> None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        metrics = self.checkin_service.compute_metrics(self.current_team_id)
        if metrics["total"] == 0:
            messagebox.showwarning(
                "No tasks", "Add tasks before submitting a check-in."
            )
            return
        errors = self.checkins_section.errors()
        if errors:
            messagebox.showwarning("Invalid data", "\n".join(errors))
            return
        week_start, week_end = self._current_week_range()
        if self.checkin_service.checkin_exists(self.current_team_id, week_start):
            messagebox.showwarning(
                "Already submitted", "This week already has a check-in."
            )
            return
        data = self.checkins_section.get_data()
        self.checkin_service.create_checkin(
            self.current_team_id,
            week_start,
            week_end,
            data["status"],
            data["wins"],
            data["risks"],
            data["next_goal"],
            data.get("help_needed") or None,
            metrics,
        )
        self.checkins_section.clear_form()
        self._refresh_checkins()

    def _add_comment(self) -> None:
        if not self.current_roadmap_id:
            messagebox.showwarning("No roadmap", "Create a roadmap first.")
            return
        selection = self.task_section.selected_member_label()
        if not selection:
            messagebox.showwarning("No member", "Select a member for this comment.")
            return
        user_name = selection.split(" ", 1)[1]
        modal = Modal(self, "Add Comment")
        form = CommentForm()
        form.render(modal.body)

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            text = form.get_data()["text"]
            self.roadmap_service.add_roadmap_comment(
                self.current_roadmap_id, user_name, text, "comment"
            )
            modal.destroy()
            self._refresh_comments()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _refresh_updates(self) -> None:
        task_id = self._selected_task_id()
        if not task_id:
            self.task_section.set_update_rows([])
            return
        updates = self.task_service.list_updates_for_task(task_id)
        rows = [(u["user"], u["text"], u["created_at"]) for u in updates]
        self.task_section.set_update_rows(rows)
        self._show_task_details(task_id, updates)

    def _refresh_team_members(self) -> None:
        if not self.current_team_id:
            return
        members = self.team_service.list_team_members(self.current_team_id)
        choices = [f"{m['id']} {m['name']}" for m in members]
        self.task_section.set_member_choices(choices)
        if choices:
            self.task_section.member_select.current(0)

    def _refresh_stats(self) -> None:
        status = self.current_roadmap_status or "-"
        done = len(
            [t for t in getattr(self, "tasks_cache", []) if t["status"] == "Done"]
        )
        self.stats_row.set_values(status, done)

    def _selected_phase_id(self) -> int | None:
        selection = self.roadmap_section.tree.selection()
        if not selection:
            return None
        item_id = selection[0]
        if item_id.startswith("phase-"):
            return int(item_id.split("-", 1)[1])
        if item_id.startswith("task-"):
            parent = self.roadmap_section.tree.parent(item_id)
            if parent.startswith("phase-"):
                return int(parent.split("-", 1)[1])
        return None

    def _selected_task_id(self) -> int | None:
        return self.task_section.selected_task_id()

    def _show_task_details(self, task_id: int, updates: list[dict]) -> None:
        row = None
        for task in getattr(self, "tasks_cache", []):
            if task["id"] == task_id:
                row = task
                break
        if not row:
            return
        self.drawer.clear()
        team = (
            self.team_service.get_team(self.current_team_id)
            if self.current_team_id
            else None
        )
        if team:
            self._render_team_header(team)
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
                row,
                text=f"{upd['user']}: {upd['text']}",
                wraplength=200,
                justify="left",
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
        current = self.roadmap_section.tree.item(f"phase-{phase_id}", "text").replace(
            "Phase: ", ""
        )
        name_entry.insert(0, current)

        def save() -> None:
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing data", "Enter a phase name.")
                return
            self.roadmap_service.update_phase(phase_id, name)
            modal.destroy()
            self._refresh_roadmap_tree()

        bind_modal_keys(modal, save)
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
        row = self.task_section.task_table.item(
            self.task_section.task_table.selection()[0], "values"
        )
        modal = Modal(self, "Edit Task")
        form = TaskForm()
        form.render(modal.body, columns=1)
        form.set_data({"title": row[1], "weight": row[3]})

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            self.roadmap_service.update_task_details(
                task_id, data["title"], int(data["weight"])
            )
            modal.destroy()
            self._refresh_roadmap_tree()
            self._refresh_task_list()

        bind_modal_keys(modal, save)
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
        team = (
            self.team_service.get_team(self.current_team_id)
            if self.current_team_id
            else None
        )
        principal = team.get("principal_name") if team else None
        title = "Team Charts"
        if team:
            title = f"{team['name']} Charts"
        if principal:
            title = f"{title} · Principal: {principal}"
        show_charts_window(self, title, tasks)
