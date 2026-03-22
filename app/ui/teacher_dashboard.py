from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from app.services.checkin import CheckinService
from app.services.classes import ClassService
from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService
from app.ui.charts import show_reports_window
from app.ui.components import Modal, bind_modal_keys
from app.ui.dashboard_base import DashboardBase
from app.ui.teacher import (
    ClassSetupSection,
    CheckinsSection,
    RoadmapReviewSection,
    StudentRosterSection,
    TeacherStatsRow,
    TeamSection,
)
from app.ui.forms import ApprovalNoteForm, CommentForm, StudentForm


class TeacherDashboard(DashboardBase):
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
        self.class_id: int | None = None
        self.teams_cache: list[dict] = []
        self.class_service = class_service
        self.checkin_service = checkin_service
        self.team_service = team_service
        self.roadmap_service = roadmap_service
        self.task_service = task_service

        super().__init__(master, "Teacher Dashboard", on_back)

        self._refresh_students()
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_checkins()
        self._refresh_stats()

    def build_layout(self) -> None:
        content = self.shell.content
        self.configure_content_grid((1, 2, 0))

        self.stats_row = TeacherStatsRow(content)
        self.stats_row.grid(row=0, column=0, columnspan=2, sticky="ew", pady=8)

        self.class_section = ClassSetupSection(content, self._create_class)
        self.class_section.grid(row=1, column=0, sticky="new", padx=8, pady=8)

        self.student_section = StudentRosterSection(
            content,
            self._add_student,
            self._edit_student,
            self._delete_student,
            self._show_student_details,
        )
        self.student_section.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)

        tabs = ttk.Notebook(content)
        tabs.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=8, pady=8)

        self.team_section = TeamSection(
            tabs,
            self._create_team,
            self._add_team_member,
            self._send_invite,
            self._set_principal,
            self._set_member_role,
            self._edit_team,
            self._delete_team,
            self._refresh_team_members,
        )
        tabs.add(self.team_section, text="Teams")

        self.roadmap_section = RoadmapReviewSection(
            tabs, self._add_comment, self._approve_roadmap, self._refresh_comments
        )
        tabs.add(self.roadmap_section, text="Roadmaps")

        self.checkins_section = CheckinsSection(
            tabs,
            self._refresh_checkin_comments,
            self._add_checkin_comment,
            self._approve_checkin,
        )
        tabs.add(self.checkins_section, text="Check-ins")

        self.mount_drawer(row=1, column=2, rowspan=2)

        self.add_topbar_button("View Charts", self._show_charts)

    def _create_class(self) -> None:
        errors = self.class_section.errors()
        if errors:
            messagebox.showwarning("Invalid data", "\n".join(errors))
            return
        name = self.class_section.get_name()
        term = self.class_section.get_term()
        if not name or not term:
            messagebox.showwarning("Missing data", "Enter a class name and term.")
            return
        self.class_id = self.class_service.create_class(name, term)
        self.class_section.set_status(f"Active class: {name} ({term})")
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _add_student(self) -> None:
        errors = self.student_section.errors()
        if errors:
            messagebox.showwarning("Invalid data", "\n".join(errors))
            return
        name = self.student_section.get_name()
        email = self.student_section.get_email()
        self.class_service.create_user(name, email, "student")
        self.student_section.clear_form()
        self._refresh_students()
        self._refresh_stats()

    def _create_team(self) -> None:
        if not self.class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return
        name = self.team_section.get_team_name()
        if not name:
            messagebox.showwarning("Missing data", "Enter a team name.")
            return
        self.team_service.create_team(self.class_id, name, None)
        self.team_section.clear_team_name()
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _add_team_member(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.team_section.selected_member_label()
        if not selection:
            messagebox.showwarning("No student", "Select a student to add.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.team_service.add_team_member(team_id, user_id)
        self._refresh_team_members()

    def _send_invite(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.team_section.selected_member_label()
        if not selection:
            messagebox.showwarning("No student", "Select a student to invite.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.team_service.create_invitation(team_id, user_id)
        self._refresh_team_invitations()

    def _set_principal(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        selection = self.team_section.selected_principal_label()
        if not selection:
            messagebox.showwarning("No student", "Select a principal student.")
            return
        user_id = int(selection.split(" ", 1)[0])
        self.team_service.update_team_principal(team_id, user_id)
        self._refresh_teams()

    def _set_member_role(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        user_id = self.team_section.selected_member_id()
        if not user_id:
            messagebox.showwarning("No member", "Select a team member.")
            return
        role = self.team_section.selected_role()
        if not role:
            messagebox.showwarning("No role", "Select a role.")
            return
        self.team_service.set_member_role(team_id, user_id, role)
        self._refresh_team_members()

    def _approve_roadmap(self) -> None:
        item = self.roadmap_section.roadmap_table.selection()
        if not item:
            messagebox.showwarning("No roadmap", "Select a roadmap to approve.")
            return
        roadmap_id = int(self.roadmap_section.roadmap_table.item(item[0], "values")[0])
        modal = Modal(self, "Approval Note")
        form = ApprovalNoteForm()
        form.render(modal.body)

        def save() -> None:
            text = form.get_data()["text"]
            if text:
                self.roadmap_service.add_roadmap_comment(
                    roadmap_id, "Teacher", text, "approval"
                )
            self.roadmap_service.approve_roadmap(roadmap_id)
            modal.destroy()
            self._refresh_roadmaps()
            self._refresh_comments()
            self._refresh_stats()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Approve", command=save).pack(
            side="right", padx=4
        )

    def _add_comment(self) -> None:
        roadmap_id = self._selected_roadmap_id()
        if not roadmap_id:
            messagebox.showwarning("No roadmap", "Select a roadmap first.")
            return
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
                roadmap_id, "Teacher", text, "comment"
            )
            modal.destroy()
            self._refresh_comments()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _refresh_students(self) -> None:
        students = self.class_service.list_users(role="student")
        rows = [(s["id"], s["name"], s["email"]) for s in students]
        self.student_section.set_rows(rows)
        choices = [f"{s['id']} {s['name']}" for s in students]
        self.team_section.set_student_choices(choices)

    def _refresh_teams(self) -> None:
        if not self.class_id:
            self.team_section.set_team_rows([])
            return
        self.teams_cache = self.team_service.list_teams(self.class_id)
        rows = []
        for team in self.teams_cache:
            principal = team["principal_name"] or "-"
            rows.append((team["id"], team["name"], principal))
        self.team_section.set_team_rows(rows)
        if rows:
            first = self.team_section.team_table.get_children()[0]
            self.team_section.team_table.selection_set(first)
            self._refresh_team_members()
        self._show_team_details()

    def _refresh_team_members(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.team_section.set_member_rows([])
            return
        members = self.team_service.list_team_members(team_id)
        rows = [(m["id"], m["name"], m["email"], m["role"]) for m in members]
        self.team_section.set_member_rows(rows)
        self._show_team_details()
        self._refresh_team_invitations()

    def _refresh_team_invitations(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.team_section.set_invite_rows([])
            return
        invites = self.team_service.list_invitations_for_team(team_id)
        rows = [(i["id"], i["user"], i["status"]) for i in invites]
        self.team_section.set_invite_rows(rows)

    def _refresh_roadmaps(self) -> None:
        if not self.class_id:
            self.roadmap_section.set_roadmap_rows([])
            return
        roadmaps = self.roadmap_service.list_roadmaps_for_class(self.class_id)
        rows = [
            (r["id"], r["team"], r["principal"] or "-", r["status"]) for r in roadmaps
        ]
        self.roadmap_section.set_roadmap_rows(rows)
        self._refresh_comments()

    def _refresh_checkins(self) -> None:
        if not self.class_id:
            self.checkins_section.set_rows([])
            return
        checkins = self.checkin_service.list_checkins_for_class(self.class_id)
        rows = [
            (
                c["id"],
                c["team"],
                f"{c['week_start']} → {c['week_end']}",
                c["status"],
                f"{c['percent']}%",
                c["submitted_at"],
            )
            for c in checkins
        ]
        self.checkins_section.set_rows(rows)
        self._refresh_checkin_comments()

    def _refresh_stats(self) -> None:
        students = self.class_service.list_users(role="student")
        teams = self.team_service.list_teams(self.class_id) if self.class_id else []
        roadmaps = (
            self.roadmap_service.list_roadmaps_for_class(self.class_id)
            if self.class_id
            else []
        )
        self.stats_row.set_counts(len(students), len(teams), len(roadmaps))

    def _show_charts(self) -> None:
        if not self.class_id:
            messagebox.showwarning("No class", "Create a class first.")
            return
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team to view reports.")
            return
        team = self.team_service.get_team(team_id)
        team_name = team.get("name", "Team") if team else "Team"
        tasks = self.task_service.list_tasks_for_team(team_id)
        checkins = self.checkin_service.list_checkins_for_team(team_id)
        title = "Team Reports"
        principal = team.get("principal_name") if team else None
        if principal:
            title = f"{title} · Principal: {principal}"
        show_reports_window(self, title, team_name, tasks, checkins)

    def _selected_team_id(self) -> int | None:
        return self.team_section.selected_team_id()

    def _selected_roadmap_id(self) -> int | None:
        return self.roadmap_section.selected_roadmap_id()

    def _refresh_comments(self) -> None:
        roadmap_id = self._selected_roadmap_id()
        if not roadmap_id:
            self.roadmap_section.set_comment_rows([])
            return
        self._show_roadmap_details()
        comments = self.roadmap_service.list_roadmap_comments(roadmap_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        self.roadmap_section.set_comment_rows(rows)

    def _refresh_checkin_comments(self) -> None:
        checkin_id = self.checkins_section.selected_id()
        if not checkin_id:
            self.checkins_section.set_comment_rows([])
            return
        self._show_checkin_details()
        comments = self.checkin_service.list_checkin_comments(checkin_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        self.checkins_section.set_comment_rows(rows)

    def _show_roadmap_details(self) -> None:
        selection = self.roadmap_section.roadmap_table.selection()
        if not selection:
            return
        row = self.roadmap_section.roadmap_table.item(selection[0], "values")
        self.drawer.clear()
        team_id = self._selected_team_id()
        if team_id:
            self._render_team_header()
        roadmap_id, team_name, principal, status = row
        tk.Label(self.drawer.body, text=f"Roadmap #{roadmap_id}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Team: {team_name}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Principal: {principal}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Status: {status}").pack(anchor="w")

    def _selected_student_id(self) -> int | None:
        return self.student_section.selected_id()

    def _show_student_details(self) -> None:
        student_id = self._selected_student_id()
        if not student_id:
            return
        row = self.student_section.selected_row()
        if not row:
            return
        self.drawer.clear()
        self._render_team_header()
        tk.Label(self.drawer.body, text=f"Student #{row[0]}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Name: {row[1]}").pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Email: {row[2]}").pack(anchor="w")
        tk.Button(self.drawer.actions, text="Edit", command=self._edit_student).pack(
            side="left", padx=4
        )
        tk.Button(
            self.drawer.actions, text="Delete", command=self._delete_student
        ).pack(side="left", padx=4)

    def _show_team_details(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            return
        row = self.team_section.selected_team_row()
        if not row:
            return
        self.drawer.clear()
        self._render_team_header(row)
        tk.Button(self.drawer.actions, text="Edit", command=self._edit_team).pack(
            side="left", padx=4
        )
        tk.Button(self.drawer.actions, text="Delete", command=self._delete_team).pack(
            side="left", padx=4
        )

    def _show_checkin_details(self) -> None:
        checkin_id = self.checkins_section.selected_id()
        if not checkin_id:
            return
        checkin = self.checkin_service.get_checkin(checkin_id)
        if not checkin:
            return
        team = self.team_service.get_team(checkin["team_id"])
        self.drawer.clear()
        if team:
            self._render_team_header(
                (team["id"], team["name"], team.get("principal_name") or "-")
            )
        tk.Label(self.drawer.body, text=f"Check-in #{checkin['id']}").pack(anchor="w")
        tk.Label(
            self.drawer.body,
            text=f"Week: {checkin['week_start']} → {checkin['week_end']}",
        ).pack(anchor="w")
        tk.Label(self.drawer.body, text=f"Status: {checkin['status']}").pack(anchor="w")
        tk.Label(
            self.drawer.body,
            text=f"Progress: {checkin['metrics_percent']}% "
            f"({checkin['metrics_done']}/{checkin['metrics_total']})",
        ).pack(anchor="w")
        tk.Label(self.drawer.body, text="Wins").pack(anchor="w", pady=(8, 0))
        tk.Label(
            self.drawer.body, text=checkin["wins"], wraplength=220, justify="left"
        ).pack(anchor="w")
        tk.Label(self.drawer.body, text="Risks").pack(anchor="w", pady=(8, 0))
        tk.Label(
            self.drawer.body, text=checkin["risks"], wraplength=220, justify="left"
        ).pack(anchor="w")
        tk.Label(self.drawer.body, text="Next Goal").pack(anchor="w", pady=(8, 0))
        tk.Label(
            self.drawer.body, text=checkin["next_goal"], wraplength=220, justify="left"
        ).pack(anchor="w")
        if checkin["help_needed"]:
            tk.Label(self.drawer.body, text="Help Needed").pack(anchor="w", pady=(8, 0))
            tk.Label(
                self.drawer.body,
                text=checkin["help_needed"],
                wraplength=220,
                justify="left",
            ).pack(anchor="w")

    def _add_checkin_comment(self) -> None:
        checkin_id = self.checkins_section.selected_id()
        if not checkin_id:
            messagebox.showwarning("No check-in", "Select a check-in first.")
            return
        modal = Modal(self, "Add Comment")
        form = CommentForm()
        form.render(modal.body)

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            text = form.get_data()["text"]
            self.checkin_service.add_checkin_comment(
                checkin_id, "Teacher", text, "comment"
            )
            modal.destroy()
            self._refresh_checkin_comments()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _approve_checkin(self) -> None:
        checkin_id = self.checkins_section.selected_id()
        if not checkin_id:
            messagebox.showwarning("No check-in", "Select a check-in first.")
            return
        modal = Modal(self, "Approval Note")
        form = ApprovalNoteForm()
        form.render(modal.body)

        def save() -> None:
            text = form.get_data()["text"]
            if text:
                self.checkin_service.add_checkin_comment(
                    checkin_id, "Teacher", text, "approval"
                )
            modal.destroy()
            self._refresh_checkin_comments()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Approve", command=save).pack(
            side="right", padx=4
        )

    def _render_team_header(self, team_row: tuple | None = None) -> None:
        if team_row:
            team_id, team_name, principal = team_row
        else:
            team_id = self._selected_team_id()
            if not team_id:
                return
            team = self.team_service.get_team(team_id)
            if not team:
                return
            team_name = team["name"]
            principal = team.get("principal_name") or "-"
        self.drawer.render_team_header(team_id, team_name, principal)

    def _edit_student(self) -> None:
        student_id = self._selected_student_id()
        if not student_id:
            messagebox.showwarning("No student", "Select a student first.")
            return
        row = self.student_section.selected_row()
        if not row:
            return
        modal = Modal(self, "Edit Student")
        form = StudentForm()
        form.render(modal.body)
        form.set_data({"name": row[1], "email": row[2]})

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            name = data["name"]
            email = data["email"]
            self.class_service.update_user(student_id, name, email)
            modal.destroy()
            self._refresh_students()
            self._refresh_stats()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _delete_student(self) -> None:
        student_id = self._selected_student_id()
        if not student_id:
            messagebox.showwarning("No student", "Select a student first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this student?"):
            return
        self.class_service.delete_user(student_id)
        self._refresh_students()
        self._refresh_team_members()
        self._refresh_stats()

    def _edit_team(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        row = self.team_section.selected_team_row()
        if not row:
            return
        modal = Modal(self, "Edit Team")
        tk.Label(modal.body, text="Team Name").grid(row=0, column=0, sticky="w")
        name_entry = tk.Entry(modal.body, width=24)
        name_entry.grid(row=0, column=1, padx=6, pady=4)
        name_entry.insert(0, row[1])

        def save() -> None:
            name = name_entry.get().strip()
            if not name:
                messagebox.showwarning("Missing data", "Enter a team name.")
                return
            self.team_service.update_team(team_id, name)
            modal.destroy()
            self._refresh_teams()

        bind_modal_keys(modal, save)
        tk.Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        tk.Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _delete_team(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return
        if not messagebox.askyesno("Confirm", "Delete this team?"):
            return
        self.team_service.delete_team(team_id)
        self._refresh_teams()
        self._refresh_team_members()
        self._refresh_roadmaps()
        self._refresh_stats()
