from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.services.checkin import CheckinService
from app.services.classes import ClassService
from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService
from app.services.auth import AuthenticatedUser
from app.ui.charts import show_reports_window
from app.ui.components import Button, Modal, bind_modal_keys
from app.ui.dashboard_base import DashboardBase
from app.ui.teacher.pages.home import TeacherHomePage
from app.ui.teacher.pages.classes import TeacherClassesPage
from app.ui.teacher.pages.teams import TeacherTeamsPage
from app.ui.teacher.pages.roadmaps import TeacherRoadmapsPage
from app.ui.teacher.pages.checkins import TeacherCheckinsPage
from app.ui.teacher.pages.students import TeacherStudentsPage
from app.ui.vm.helpers import (
    Choice,
    Notifier,
    map_choices,
    set_table_with_placeholder,
    validate_or_warn,
)
from app.ui.teacher import (
    ClassSetupSection,
    CheckinsSection,
    RoadmapReviewSection,
    StudentRosterSection,
    TeacherStatsRow,
    TeamSection,
)
from app.ui.forms import ApprovalNoteForm, CommentForm, StudentForm, TeamForm


class TeacherDashboard(DashboardBase):
    def __init__(
        self,
        master,
        class_service: ClassService,
        checkin_service: CheckinService,
        team_service: TeamService,
        roadmap_service: RoadmapService,
        task_service: TaskService,
        current_user: AuthenticatedUser,
        demo_mode: bool,
        on_back,
    ) -> None:
        self.class_id: int | None = None
        self.teams_cache: list[dict] = []
        self.student_choices: dict[str, Choice] = {}
        self.current_user = current_user
        self.demo_mode = demo_mode
        self.class_service = class_service
        self.checkin_service = checkin_service
        self.team_service = team_service
        self.roadmap_service = roadmap_service
        self.task_service = task_service
        self.notifier = Notifier()

        nav_items = [
            ("Dashboard", "dashboard"),
            ("Classes", "classes"),
            ("Students", "students"),
            ("Teams", "teams"),
            ("Roadmaps", "roadmaps"),
            ("Check-ins", "checkins"),
            ("Reports", "reports"),
        ]
        super().__init__(
            master,
            "Teacher Dashboard",
            on_back,
            nav_items=nav_items,
            on_nav=self._on_nav,
        )

        self._autoselect_class()
        self._services = {
            "class": class_service,
            "checkin": checkin_service,
            "team": team_service,
            "roadmap": roadmap_service,
            "task": task_service,
        }
        self._pages_cache: dict[str, tk.Frame] = {}
        self._current_page: str | None = None
        self._navigate("dashboard")

    def _autoselect_class(self) -> None:
        # If a class already exists, select the first one and update status.
        classes = (
            # NOTE: Making sure the service class is loaded
            self.class_service.list_classes(owner_user_id=self.current_user.id)
            if hasattr(self.class_service, "list_classes")
            else []
        )
        if classes:
            first = classes[0]
            self.class_id = first["id"] if isinstance(first, dict) else first[0]
            name = first.get("name") if isinstance(first, dict) else first[1]
            term = first.get("term") if isinstance(first, dict) else first[2]
            if hasattr(self, "class_section"):
                self.class_section.set_status(f"Active class: {name} ({term})")
        else:
            self.class_id = None

    def build_layout(self) -> None:
        # Content will be swapped per page; nothing to build here.
        self.configure_content_grid((1, 1, 0))
        if self.demo_mode:
            self.add_demo_button()
        self.add_topbar_button("View Charts", self._show_charts)

    def _on_nav(self, key: str) -> None:
        if key == "reports":
            self._show_charts()
            return
        self._navigate(key)

    def _navigate(self, route: str) -> None:
        if route == self._current_page:
            return
        page = self._create_page(route)
        if not page:
            return
        self.swap_content(page)
        self._current_page = route

    def _create_page(self, route: str) -> tk.Frame | None:
        if route == "dashboard":
            return TeacherHomePage(self.shell.content, self._services, self.class_id)
        if route == "classes":
            return TeacherClassesPage(
                self.shell.content,
                self._services,
                owner_user_id=self.current_user.id,
                current_class_id=self.class_id,
                on_select_class=self._set_active_class,
            )
        if route == "students":
            return TeacherStudentsPage(self.shell.content, self._services)
        if route == "teams":
            return TeacherTeamsPage(self.shell.content, self._services, self.class_id)
        if route == "roadmaps":
            return TeacherRoadmapsPage(
                self.shell.content, self._services, self.class_id
            )
        if route == "checkins":
            return TeacherCheckinsPage(
                self.shell.content, self._services, self.class_id
            )
        return None

    def _set_active_class(self, class_id: int) -> None:
        self.class_id = class_id

    def _create_class(self) -> None:
        if not validate_or_warn(self.class_section.errors(), self.notifier):
            return
        name = self.class_section.get_name()
        term = self.class_section.get_term()
        if not name or not term:
            self.notifier.warn("Enter a class name and term.", "Missing data")
            return
        self.class_id = self.class_service.create_class(
            name,
            term,
            owner_user_id=self.current_user.id,
        )
        self.class_section.set_status(f"Active class: {name} ({term})")
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _add_student(self, data: dict) -> None:
        self.class_service.create_user(data["name"], data["email"], "student")
        self._refresh_students()
        self._refresh_stats()

    def _create_team(self, data: dict) -> None:
        if not self.class_id:
            self.notifier.warn("Create a class first.", "No class")
            return
        name = data["name"]
        self.team_service.create_team(self.class_id, name, None)
        self._refresh_teams()
        self._refresh_roadmaps()
        self._refresh_stats()

    def _team_create_modal(self) -> None:
        if not self.class_id:
            self.notifier.warn("Create a class first.", "No class")
            return
        modal = Modal(self, "Create Team")
        form = TeamForm()
        form.render(modal.body, columns=1)

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            modal.destroy()
            self._create_team(data)

        bind_modal_keys(modal, save)
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Create", command=save).pack(side="right", padx=4)

    def _add_team_member(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.notifier.warn("Select a team first.", "No team")
            return
        selection = self.team_section.selected_member_label()
        if not selection:
            self.notifier.warn("Select a student to add.", "No student")
            return
        choice = self.student_choices.get(selection)
        if not choice:
            self.notifier.warn("Selected student is unavailable.")
            return
        user_id = choice.id
        self.team_service.add_team_member(team_id, user_id)
        self._refresh_team_members()

    def _send_invite(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.notifier.warn("Select a team first.", "No team")
            return
        selection = self.team_section.selected_member_label()
        if not selection:
            self.notifier.warn("Select a student to invite.", "No student")
            return
        choice = self.student_choices.get(selection)
        if not choice:
            self.notifier.warn("Selected student is unavailable.")
            return
        user_id = choice.id
        self.team_service.create_invitation(team_id, user_id)
        self._refresh_team_invitations()

    def _set_principal(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.notifier.warn("Select a team first.", "No team")
            return
        selection = self.team_section.selected_principal_label()
        if not selection:
            self.notifier.warn("Select a principal student.", "No student")
            return
        choice = self.student_choices.get(selection)
        if not choice:
            self.notifier.warn("Selected student is unavailable.")
            return
        user_id = choice.id
        self.team_service.update_team_principal(team_id, user_id)
        self._refresh_teams()

    def _set_member_role(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            self.notifier.warn("Select a team first.", "No team")
            return
        user_id = self.team_section.selected_member_id()
        if not user_id:
            self.notifier.warn("Select a team member.", "No member")
            return
        role = self.team_section.selected_role()
        if not role:
            self.notifier.warn("Select a role.", "No role")
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
                    roadmap_id, self.current_user.name, text, "approval"
                )
            self.roadmap_service.approve_roadmap(roadmap_id)
            modal.destroy()
            self._refresh_roadmaps()
            self._refresh_comments()
            self._refresh_stats()

        bind_modal_keys(modal, save)
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Approve", command=save).pack(side="right", padx=4)

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
                roadmap_id, self.current_user.name, text, "comment"
            )
            modal.destroy()
            self._refresh_comments()

        bind_modal_keys(modal, save)
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

    def _refresh_students(self) -> None:
        students = self.class_service.list_users(role="student")
        rows = [(s["id"], s["name"], s["email"]) for s in students]
        self.student_section.set_rows(rows)
        choice_objs = [
            Choice(id=s["id"], label=f"{s['name']} (#{s['id']})") for s in students
        ]
        labels, mapping = map_choices(choice_objs)
        self.student_choices = mapping
        self.team_section.set_student_choices(labels)

    def _refresh_teams(self) -> None:
        if not self.class_id:
            set_table_with_placeholder(self.team_section.team_table, [], "No teams")
            return
        self.teams_cache = self.team_service.list_teams(self.class_id)
        rows = []
        for team in self.teams_cache:
            principal = team["principal_name"] or "-"
            rows.append((team["id"], team["name"], principal))
        set_table_with_placeholder(self.team_section.team_table, rows, "No teams")
        if rows:
            first = self.team_section.team_table.get_children()[0]
            self.team_section.team_table.selection_set(first)
            self._refresh_team_members()
        self._show_team_details()

    def _refresh_team_members(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            set_table_with_placeholder(self.team_section.member_table, [], "No members")
            return
        members = self.team_service.list_team_members(team_id)
        rows = [(m["id"], m["name"], m["email"], m["role"]) for m in members]
        set_table_with_placeholder(self.team_section.member_table, rows, "No members")
        self._show_team_details()
        self._refresh_team_invitations()

    def _refresh_team_invitations(self) -> None:
        team_id = self._selected_team_id()
        if not team_id:
            set_table_with_placeholder(self.team_section.invite_table, [], "No invites")
            return
        invites = self.team_service.list_invitations_for_team(team_id)
        rows = [(i["id"], i["user"], i["status"]) for i in invites]
        set_table_with_placeholder(self.team_section.invite_table, rows, "No invites")

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
        teams = self.team_service.list_teams(self.class_id)
        if not teams:
            messagebox.showwarning("No team", "Create a team to view reports.")
            return
        if len(teams) == 1:
            self._open_team_reports(teams[0])
            return
        self._open_team_picker(teams)

    def _open_team_picker(self, teams: list[dict]) -> None:
        modal = Modal(self, "Select Team")
        listbox = tk.Listbox(modal.body, height=min(10, len(teams)))
        for team in teams:
            principal = team.get("principal_name") or "-"
            listbox.insert(tk.END, f"#{team['id']} · {team['name']} · {principal}")
        listbox.pack(fill="both", expand=True, padx=6, pady=6)

        def choose_and_close() -> None:
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("No team", "Select a team to view reports.")
                return
            team = teams[selection[0]]
            modal.destroy()
            self._open_team_reports(team)

        listbox.bind("<Double-Button-1>", lambda _e: choose_and_close())
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Open", command=choose_and_close).pack(
            side="right", padx=4
        )

    def _open_team_reports(self, team: dict) -> None:
        team_id = team["id"]
        team_name = team.get("name", "Team")
        tasks = self.task_service.list_tasks_for_team(team_id)
        checkins = self.checkin_service.list_checkins_for_team(team_id)
        title = "Team Reports"
        principal = team.get("principal_name")
        if principal:
            title = f"{title} · Principal: {principal}"
        show_reports_window(self, title, team_name, tasks, checkins)

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
        Button(
            self.drawer.actions,
            text="Edit",
            command=lambda sid=row[0], name=row[1], email=row[2]: (
                self._student_edit_modal(sid, name, email)
            ),
        ).pack(side="left", padx=4)
        Button(
            self.drawer.actions,
            text="Delete",
            command=lambda sid=row[0]: self._delete_student(sid),
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
        Button(self.drawer.actions, text="Edit", command=self._edit_team).pack(
            side="left", padx=4
        )
        Button(self.drawer.actions, text="Delete", command=self._delete_team).pack(
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
                checkin_id, self.current_user.name, text, "comment"
            )
            modal.destroy()
            self._refresh_checkin_comments()

        bind_modal_keys(modal, save)
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

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
                    checkin_id, self.current_user.name, text, "approval"
                )
            modal.destroy()
            self._refresh_checkin_comments()

        bind_modal_keys(modal, save)
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Approve", command=save).pack(side="right", padx=4)

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

    def _edit_student(self, student_id: int, data: dict) -> None:
        self.class_service.update_user(student_id, data["name"], data["email"])
        self._refresh_students()
        self._refresh_stats()

    def _delete_student(self, student_id: int) -> None:
        self.class_service.delete_user(student_id)
        self._refresh_students()
        self._refresh_team_members()
        self._refresh_stats()

    def _student_edit_modal(self, student_id: int, name: str, email: str) -> None:
        modal = Modal(self, "Edit Student")
        form = StudentForm()
        form.render(modal.body)
        form.set_data({"name": name, "email": email})

        def save() -> None:
            errors = form.validate()
            if errors:
                messagebox.showwarning("Invalid data", "\n".join(errors))
                return
            data = form.get_data()
            self._edit_student(student_id, data)
            modal.destroy()

        bind_modal_keys(modal, save)
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

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
        Button(modal.actions, text="Cancel", command=modal.destroy).pack(
            side="right", padx=4
        )
        Button(modal.actions, text="Save", command=save).pack(side="right", padx=4)

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
