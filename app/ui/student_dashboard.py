from __future__ import annotations

import tkinter as tk
from datetime import date, timedelta
from tkinter import messagebox

from app.services.auth import AuthenticatedUser
from app.services.checkin import CheckinService
from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService
from app.services.classes import ClassService
from app.services.validation import validate_roadmap
from app.ui.charts import show_reports_window
from app.ui.components import FormDialog, Modal, add_modal_actions
from app.ui.dashboard_base import DashboardBase
from app.ui.forms import CommentForm, TaskForm
from app.ui.student.pages import StudentOverviewPage, StudentSectionPage
from app.ui.student import (
    RoadmapBuilderSection,
    StudentCheckinsSection,
    StudentCommentsSection,
    TaskSection,
)
from app.design_system.typography import Typography
from app.ui.vm.helpers import (
    Choice,
    Notifier,
    map_choices,
    resolve_selected,
    set_table_with_placeholder,
    validate_or_warn,
)


FONT_FAMILY = Typography.primary_font_family()


class StudentDashboard(DashboardBase):
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
        self.current_team_id: int | None = None
        self.current_roadmap_id: int | None = None
        self.current_roadmap_status: str | None = None
        self.active_student_id: int | None = current_user.id
        self.current_user = current_user
        self.demo_mode = demo_mode
        self.notifier = Notifier()
        self.class_service = class_service
        self.checkin_service = checkin_service
        self.team_service = team_service
        self.roadmap_service = roadmap_service
        self.task_service = task_service
        self.student_choices: dict[str, Choice] = {}
        self.team_choices: dict[str, Choice] = {}
        self.member_choices: dict[str, Choice] = {}
        self._current_page: str | None = None
        self._pages: dict[str, tk.Frame] = {}

        nav_items = [
            ("Overview", "overview"),
            ("Roadmap", "roadmap"),
            ("Tasks", "tasks"),
            ("Check-ins", "checkins"),
            ("Comments", "comments"),
            ("Reports", "reports"),
        ]

        super().__init__(
            master,
            "Student Workspace",
            on_back,
            nav_items=nav_items,
            on_nav=self._on_nav,
        )

        if self.demo_mode:
            self.add_demo_button()
        self.add_topbar_button("View Charts", self._show_charts)
        self._refresh_students()
        self._refresh_invitations()
        self._refresh_teams()
        self._navigate("overview")

    def build_layout(self) -> None:
        content = self.shell.content
        content.grid_rowconfigure(0, weight=1)
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=0, minsize=260)

        self.page_host = tk.Frame(content, bg=content["bg"])
        self.page_host.grid(row=0, column=0, sticky="nsew")

        overview_page = StudentOverviewPage(self.page_host, self._navigate)
        self.stats_row = overview_page.stats_row

        roadmap_page = StudentSectionPage(
            self.page_host,
            title="Roadmap",
            subtitle="Manage invites, phases, and task planning.",
        )
        self.roadmap_section = RoadmapBuilderSection(
            roadmap_page.body,
            self._set_active_student,
            self._accept_invite,
            self._decline_invite,
            self._create_team,
            self._invite_student,
            self._load_roadmap,
            self._add_phase,
            self._edit_phase,
            self._delete_phase,
            self._add_task,
            self._edit_task,
            self._delete_task,
            self._submit_roadmap,
            self._show_charts,
            show_student_selector=False,
        )
        self.roadmap_section.pack(fill="both", expand=True)

        tasks_page = StudentSectionPage(
            self.page_host,
            title="Tasks",
            subtitle="Track implementation progress and updates.",
        )
        self.task_section = TaskSection(
            tasks_page.body,
            self._refresh_updates,
            self._set_task_status,
            self._add_update,
        )
        self.task_section.pack(fill="both", expand=True)

        comments_page = StudentSectionPage(
            self.page_host,
            title="Comments",
            subtitle="Roadmap feedback and discussion history.",
        )
        self.comments_section = StudentCommentsSection(
            comments_page.body,
            self._add_comment,
        )
        self.comments_section.pack(fill="both", expand=True)

        checkins_page = StudentSectionPage(
            self.page_host,
            title="Check-ins",
            subtitle="Weekly status reports and progress metrics.",
        )
        self.checkins_section = StudentCheckinsSection(
            checkins_page.body,
            self._submit_checkin,
        )
        self.checkins_section.pack(fill="both", expand=True)

        self._pages = {
            "overview": overview_page,
            "roadmap": roadmap_page,
            "tasks": tasks_page,
            "checkins": checkins_page,
            "comments": comments_page,
        }

        self.drawer.grid(row=0, column=1, sticky="nsew", padx=(8, 8), pady=8)

    def _on_nav(self, route: str) -> None:
        if route == "reports":
            self._show_charts()
            return
        self._navigate(route)

    def _navigate(self, route: str) -> None:
        page = self._pages.get(route)
        if page is None or route == self._current_page:
            return

        for frame in self._pages.values():
            frame.pack_forget()

        page.pack(fill="both", expand=True)
        self._current_page = route

    def _refresh_teams(self) -> None:
        teams = (
            self.team_service.list_teams_for_user(self.active_student_id)
            if self.active_student_id
            else []
        )
        choice_objs = []
        for team in teams:
            principal = team.get("principal_name") or "Unassigned"
            label = f"{team['name']} · Principal: {principal}"
            choice_objs.append(
                Choice(
                    id=team["id"],
                    label=label,
                    extra={"principal": principal, "name": team["name"]},
                )
            )
        labels, mapping = map_choices(choice_objs)
        self.team_choices = mapping
        self.roadmap_section.set_team_choices(labels)
        if self.team_choices:
            self.roadmap_section.team_select.current(0)
            self._load_roadmap()
        else:
            self._clear_team_context()

    def _clear_team_context(self) -> None:
        self.current_team_id = None
        self.current_roadmap_id = None
        self.current_roadmap_status = None
        self.roadmap_section.set_status("No roadmap")
        self.task_section.set_task_rows([])
        self.comments_section.set_comment_rows([])
        self.task_section.set_update_rows([])
        self.roadmap_section.clear_tree()
        self.checkins_section.set_rows([])
        self.checkins_section.set_progress(0, 0, 0)

    def _refresh_students(self) -> None:
        self.active_student_id = self.current_user.id
        label = f"{self.current_user.name} (#{self.current_user.id})"
        self.student_choices = {label: Choice(id=self.current_user.id, label=label)}
        self.roadmap_section.set_student_choices([label])

    def _set_active_student(self) -> None:
        self.active_student_id = self.current_user.id
        self._refresh_invitations()
        self._refresh_teams()

    def _refresh_invitations(self) -> None:
        if not self.active_student_id:
            self.roadmap_section.set_invite_rows([])
            return
        invites = self.team_service.list_invitations_for_user(self.active_student_id)
        rows = [(i["id"], i["team"], i["status"]) for i in invites]
        self.roadmap_section.set_invite_rows(rows)

    def _class_options_for_team_creation(self) -> tuple[list[str], dict[str, int]]:
        classes = self.class_service.list_classes()
        options: list[str] = []
        mapping: dict[str, int] = {}
        for class_item in classes:
            label = f"{class_item['name']} ({class_item['term']})"
            options.append(label)
            mapping[label] = int(class_item["id"])
        return options, mapping

    def _create_team(self) -> None:
        class_options, class_mapping = self._class_options_for_team_creation()
        if not class_options:
            messagebox.showwarning("No classes", "No classes are available yet.")
            return

        dialog = FormDialog(
            self,
            title="Create Team",
            subtitle="Create a team and become its principal.",
        )
        dialog.add_text("team_name", label="Team Name")
        dialog.add_select("class", label="Class", values=class_options)

        def save() -> None:
            team_name = dialog.value("team_name")
            class_label = dialog.value("class")
            class_id = class_mapping.get(class_label)

            if not team_name:
                messagebox.showwarning("Missing data", "Enter a team name.")
                return
            if not class_id:
                messagebox.showwarning("Missing class", "Select a class.")
                return

            team_id = self.team_service.create_team(
                class_id,
                team_name,
                self.current_user.id,
            )
            self.team_service.update_team_principal(team_id, self.current_user.id)
            dialog.destroy()

            self._refresh_teams()
            target_label = None
            for label, choice in self.team_choices.items():
                if choice.id == team_id:
                    target_label = label
                    break
            if target_label:
                self.roadmap_section.team_select.set(target_label)
                self._load_roadmap()

        dialog.add_actions(save, confirm_text="Create")

    def _invite_student(self) -> None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return

        team = self.team_service.get_team(self.current_team_id)
        if not team or int(team.get("principal_user_id") or 0) != self.current_user.id:
            messagebox.showwarning(
                "Not allowed",
                "Only the team principal can invite students.",
            )
            return

        members = self.team_service.list_team_members(self.current_team_id)
        member_ids = {int(member["id"]) for member in members}
        students = self.class_service.list_users(role="student")
        eligible = [
            student
            for student in students
            if int(student["id"]) not in member_ids
            and int(student["id"]) != self.current_user.id
        ]
        if not eligible:
            messagebox.showwarning(
                "No eligible students",
                "All students are already on the team or unavailable.",
            )
            return

        options: list[str] = []
        mapping: dict[str, int] = {}
        for student in eligible:
            label = f"{student['name']} ({student['email']})"
            options.append(label)
            mapping[label] = int(student["id"])

        dialog = FormDialog(
            self,
            title="Invite Student",
            subtitle="Send a team invitation to a student.",
        )
        dialog.add_select("student", label="Student", values=options)

        def send_invite() -> None:
            label = dialog.value("student")
            user_id = mapping.get(label)
            if not user_id:
                messagebox.showwarning("No student", "Select a student to invite.")
                return
            self.team_service.create_invitation(self.current_team_id, user_id)
            dialog.destroy()
            self._refresh_invitations()
            messagebox.showinfo("Invite sent", "Student invitation has been sent.")

        dialog.add_actions(send_invite, confirm_text="Send Invite")

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
        choice = self.team_choices.get(selection)
        if not choice:
            self.notifier.warn("Selected team is unavailable.")
            return
        self.current_team_id = choice.id
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
        if not self.current_roadmap_id:
            self.roadmap_section.set_roadmap_tree([])
            return
        phases = self.roadmap_service.list_phases_with_tasks(self.current_roadmap_id)
        self.roadmap_section.set_roadmap_tree(phases)

    def _refresh_task_list(self) -> None:
        if not self.current_roadmap_id:
            set_table_with_placeholder(self.task_section.task_table, [], "No tasks")
            return
        self.tasks_cache = self.task_service.list_tasks_for_roadmap(
            self.current_roadmap_id
        )
        rows = [
            (t["id"], t["title"], t["status"], t["weight"]) for t in self.tasks_cache
        ]
        set_table_with_placeholder(self.task_section.task_table, rows, "No tasks")
        self._refresh_progress()
        self._refresh_stats()

    def _refresh_comments(self) -> None:
        if not self.current_roadmap_id:
            set_table_with_placeholder(
                self.comments_section.comment_table, [], "No comments"
            )
            return
        comments = self.roadmap_service.list_roadmap_comments(self.current_roadmap_id)
        rows = [(c["author"], c["text"], c["created_at"]) for c in comments]
        set_table_with_placeholder(
            self.comments_section.comment_table, rows, "No comments"
        )

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
                f"{c.get('metrics_percent', c.get('percent', 0))}%",
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
            self.notifier.warn("Select a task first.", "No task")
            return
        if not self.active_student_id:
            self.notifier.warn("No active user.", "Not authenticated")
            return
        if not self._current_user_is_team_member():
            self.notifier.warn("You are not a member of this team.", "Access denied")
            return
        text = self.task_section.get_update_text()
        if not text:
            self.notifier.warn("Enter an update note.", "Missing data")
            return
        self.task_service.add_update(task_id, self.active_student_id, text)
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
            self.notifier.warn("Create a roadmap first.", "No roadmap")
            return
        if not self._current_user_is_team_member():
            self.notifier.warn("You are not a member of this team.", "Access denied")
            return
        user_name = self.current_user.name
        modal = Modal(self, "Add Comment")
        form = CommentForm()
        form.render(modal.body)

        def save() -> None:
            if not validate_or_warn(form.validate(), self.notifier):
                return
            text = form.get_data()["text"]
            self.roadmap_service.add_roadmap_comment(
                self.current_roadmap_id, user_name, text, "comment"
            )
            modal.destroy()
            self._refresh_comments()

        self._add_modal_save_actions(modal, save)

    def _add_modal_save_actions(
        self, modal: Modal, on_confirm, *, confirm_text: str = "Save"
    ) -> None:
        add_modal_actions(modal, on_confirm, confirm_text=confirm_text)

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
        is_member = any(m["id"] == self.current_user.id for m in members)
        if is_member:
            label = f"{self.current_user.name} (#{self.current_user.id})"
            labels = [label]
            self.member_choices = {label: Choice(id=self.current_user.id, label=label)}
        else:
            labels = []
            self.member_choices = {}
        self.task_section.set_member_choices(labels)
        if labels:
            self.task_section.member_select.current(0)

    def _current_user_is_team_member(self) -> bool:
        if not self.current_team_id:
            return False
        members = self.team_service.list_team_members(self.current_team_id)
        return any(m["id"] == self.current_user.id for m in members)

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
            self.drawer.body, text="Recent Updates", font=(FONT_FAMILY, 10, "bold")
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

        self._add_modal_save_actions(modal, save)

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

        self._add_modal_save_actions(modal, save)

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
        team_name = team.get("name") if team else "Team"
        title = f"{team_name} Charts" if team else "Team Charts"
        if principal:
            title = f"{title} · Principal: {principal}"
        checkins = (
            self.checkin_service.list_checkins_for_team(self.current_team_id)
            if self.current_team_id
            else []
        )
        show_reports_window(self, title, team_name, tasks, checkins)
