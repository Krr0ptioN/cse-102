from __future__ import annotations

from datetime import date, timedelta
from tkinter import messagebox

from core.services import (
    AuthenticatedUser,
    CheckinService,
    ClassService,
    RoadmapService,
    TaskService,
    TeamService,
    validate_roadmap,
)
from ui.shared import DashboardBase, show_reports_window
from libs.ui_kit import FormDialog, Modal, add_modal_actions, palette
from ui.shared.forms import CommentForm
from ui.student.forms import TaskForm, CheckinForm
from ui.student.pages import (
    StudentHomePage,
    StudentRoadmapPage,
    StudentTasksPage,
    StudentCheckinsPage,
    StudentCommentsPage,
)
from ui.shared.vm.helpers import (
    Choice,
    Notifier,
    map_choices,
    set_table_with_placeholder,
    validate_or_warn,
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
        
        self.services = {
            "class": class_service,
            "checkin": checkin_service,
            "team": team_service,
            "roadmap": roadmap_service,
            "task": task_service,
        }
        
        self.student_choices: dict[str, Choice] = {}
        self.team_choices: dict[str, Choice] = {}
        self.member_choices: dict[str, Choice] = {}

        super().__init__(
            master,
            "Student Workspace",
            on_back,
        )

        if self.demo_mode:
            self.add_demo_button()
        self.add_topbar_button("View Charts", self._show_charts)
        
        # Initial context loading
        self._refresh_students()
        self._refresh_invitations()
        self._refresh_teams()
        
        # Start at overview
        self._navigate("overview")
        self.log.success("Student dashboard ready for %s", self.current_user.email)

    def build_layout(self) -> None:
        # 1. Configure Grid
        self.configure_content_grid((1, 0)) # Main content + Sidebar
        self.mount_slide_over()

        # 2. Instantiate pages (they register themselves with the registry)
        StudentHomePage(self)
        StudentRoadmapPage(self)
        StudentTasksPage(self)
        StudentCheckinsPage(self)
        StudentCommentsPage(self)
        
        # 3. Cache references to internal page sections for refresh calls
        self.roadmap_section = self.pages["roadmap"].section
        self.task_section = self.pages["tasks"].list_view
        self.comments_section = self.pages["comments"].thread
        self.checkins_section = self.pages["checkins"].list_view

        # 4. Add special navigation items
        self.shell.add_nav_item("Reports", "reports")

    def _on_nav(self, route: str) -> None:
        if route == "reports":
            self._show_charts()
            return
        self._navigate(route)

    def _refresh_teams(self) -> None:
        team_svc = self.services["team"]
        teams = (
            team_svc.list_teams_for_user(self.active_student_id)
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
        self.task_section.set_tasks([])
        self.comments_section.set_comments([])
        self.roadmap_section.clear_tree()
        self.checkins_section.set_checkins([])
        self.slide_over.clear()

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
        invites = self.services["team"].list_invitations_for_user(self.active_student_id)
        rows = [(i["id"], i["team"], i["status"]) for i in invites]
        self.roadmap_section.set_invite_rows(rows)

    def _create_team(self) -> None:
        classes = self.services["class"].list_classes()
        if not classes:
            messagebox.showwarning("No classes", "No classes are available yet.")
            return

        options = [f"{c['name']} ({c['term']})" for c in classes]
        mapping = {f"{c['name']} ({c['term']})": int(c['id']) for c in classes}

        dialog = FormDialog(self, title="Create Team")
        dialog.add_text("team_name", label="Team Name")
        dialog.add_select("class", label="Class", values=options)

        def save() -> None:
            team_name = dialog.value("team_name")
            class_id = mapping.get(dialog.value("class"))

            if not team_name or not class_id:
                messagebox.showwarning("Missing data", "Fill in all fields.")
                return

            team_id = self.services["team"].create_team(class_id, team_name, self.current_user.id)
            self.services["team"].update_team_principal(team_id, self.current_user.id)
            dialog.destroy()
            self._refresh_teams()

        dialog.add_actions(save, confirm_text="Create")

    def _invite_student(self) -> None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return

        students = self.services["class"].list_users(role="student")
        eligible = [s for s in students if int(s["id"]) != self.current_user.id]
        
        options = [f"{s['name']} ({s['email']})" for s in eligible]
        mapping = {f"{s['name']} ({s['email']})": int(s["id"]) for s in eligible}

        dialog = FormDialog(self, title="Invite Student")
        dialog.add_select("student", label="Student", values=options)

        def send() -> None:
            user_id = mapping.get(dialog.value("student"))
            if user_id:
                self.services["team"].create_invitation(self.current_team_id, user_id)
                dialog.destroy()
                self._refresh_invitations()

        dialog.add_actions(send, confirm_text="Send Invite")

    def _accept_invite(self) -> None:
        invite_id = self.roadmap_section.selected_invite_id()
        if invite_id:
            self.services["team"].accept_invitation(invite_id)
            self._refresh_invitations()
            self._refresh_teams()

    def _decline_invite(self) -> None:
        invite_id = self.roadmap_section.selected_invite_id()
        if invite_id:
            self.services["team"].decline_invitation(invite_id)
            self._refresh_invitations()

    def _load_roadmap(self) -> None:
        selection = self.roadmap_section.selected_team()
        if not selection: return
        
        choice = self.team_choices.get(selection)
        if not choice: return
        
        self.current_team_id = choice.id
        self._show_team_details()
        
        roadmap = self.services["roadmap"].get_latest_roadmap(self.current_team_id)
        if roadmap:
            self.current_roadmap_id = roadmap["id"]
            self.current_roadmap_status = roadmap["status"]
            self.roadmap_section.set_status(f"Status: {roadmap['status']}")
        else:
            self.current_roadmap_id = None
            self.current_roadmap_status = None
            self.roadmap_section.set_status("No roadmap")
            
        self._refresh_roadmap_tree()
        self._refresh_task_list()
        self._refresh_comments()
        self._refresh_checkins()
        
        # Trigger page refreshes if they are visible
        active_page = self.pages.get(self._current_page_key)
        if active_page:
            active_page.on_show()

    def _show_team_details(self) -> None:
        if not self.current_team_id: return
        team = self.services["team"].get_team(self.current_team_id)
        if not team: return
        
        self.slide_over.clear()
        self._render_team_header(team)

    def _render_team_header(self, team: dict) -> None:
        principal = team.get("principal_name") or "Unassigned"
        self.slide_over.render_team_header(team["id"], team["name"], principal)

    def _ensure_roadmap(self) -> int | None:
        if not self.current_team_id:
            messagebox.showwarning("No team", "Select a team first.")
            return None
        if not self.current_roadmap_id:
            self.current_roadmap_id = self.services["roadmap"].create_roadmap(self.current_team_id)
            self.current_roadmap_status = "Draft"
            self.roadmap_section.set_status("Status: Draft")
        return self.current_roadmap_id

    def _add_phase(self) -> None:
        roadmap_id = self._ensure_roadmap()
        if not roadmap_id: return
        name = self.roadmap_section.phase_entry.get().strip()
        if not name: return
        
        phases = self.services["roadmap"].list_phases_with_tasks(roadmap_id)
        self.services["roadmap"].create_phase(roadmap_id, name, len(phases) + 1)
        self.roadmap_section.phase_entry.delete(0, "end")
        self._refresh_roadmap_tree()

    def _add_task(self) -> None:
        roadmap_id = self._ensure_roadmap()
        if not roadmap_id: return
        
        phase_id = self._selected_phase_id()
        if not phase_id:
            messagebox.showwarning("No phase", "Select a phase first.")
            return
            
        errors = self.roadmap_section.task_errors()
        if errors:
            messagebox.showwarning("Invalid data", "\n".join(errors))
            return
            
        data = self.roadmap_section.task_data()
        self.services["roadmap"].create_task(phase_id, data["title"], int(data["weight"]))
        self.roadmap_section.clear_task()
        self._refresh_roadmap_tree()
        self._refresh_task_list()

    def _submit_roadmap(self) -> None:
        if not self.current_roadmap_id: return
        if self.current_roadmap_status != "Draft": return
        
        phases = self.services["roadmap"].list_phases_with_tasks(self.current_roadmap_id)
        payload = [{"tasks": [t["weight"] for t in p["tasks"]]} for p in phases]
        result = validate_roadmap(payload)
        
        if not result["ok"]:
            messagebox.showwarning("Invalid", result["reason"])
            return
            
        self.services["roadmap"].submit_roadmap(self.current_roadmap_id)
        self.current_roadmap_status = "Submitted"
        self.roadmap_section.set_status("Status: Submitted")

    def _refresh_roadmap_tree(self) -> None:
        if not self.current_roadmap_id:
            self.roadmap_section.set_roadmap_tree([])
            return
        phases = self.services["roadmap"].list_phases_with_tasks(self.current_roadmap_id)
        self.roadmap_section.set_roadmap_tree(phases)

    def _refresh_task_list(self) -> None:
        if not self.current_roadmap_id:
            self.task_section.set_tasks([])
            return
        tasks = self.services["task"].list_tasks_for_roadmap(self.current_roadmap_id)
        self.task_section.set_tasks([(t["id"], t["title"], t["status"], t["weight"]) for t in tasks])

    def _refresh_comments(self) -> None:
        if not self.current_roadmap_id:
            self.comments_section.set_comments([])
            return
        comments = self.services["roadmap"].list_roadmap_comments(self.current_roadmap_id)
        self.comments_section.set_comments([(c["author"], c["text"], c["created_at"]) for c in comments])

    def _refresh_checkins(self) -> None:
        if not self.current_team_id:
            self.checkins_section.set_checkins([])
            return
        checkins = self.services["checkin"].list_checkins_for_team(self.current_team_id)
        self.checkins_section.set_checkins([
            (c["id"], f"{c['week_start']} → {c['week_end']}", c["status"], f"{c.get('metrics_percent', 0)}%", c["submitted_at"])
            for c in checkins
        ])

    def _set_task_status(self, task_id: int, status: str) -> None:
        self.services["task"].update_task_status(task_id, status)
        self._refresh_task_list()

    def _add_update(self, task_id: int, text: str) -> None:
        self.services["task"].add_update(task_id, self.current_user.id, text)

    def _submit_checkin(self, text: str) -> None:
        if not self.current_team_id: return
        
        modal = Modal(self, "Weekly Check-in")
        form = CheckinForm()
        form.render(modal.body)
        
        def save() -> None:
            if not validate_or_warn(form.validate(), self.notifier): return
            
            data = form.get_data()
            metrics = self.services["checkin"].compute_metrics(self.current_team_id)
            today = date.today()
            start = today - timedelta(days=today.weekday())
            end = start + timedelta(days=6)
            
            self.services["checkin"].create_checkin(
                self.current_team_id,
                start.isoformat(),
                end.isoformat(),
                data["status"],
                data["wins"],
                data["risks"],
                data["next_goal"],
                data.get("help_needed"),
                metrics
            )
            modal.destroy()
            self._refresh_checkins()
            
        add_modal_actions(modal, save, confirm_text="Submit")

    def _add_comment(self, text: str) -> None:
        if self.current_roadmap_id:
            self.services["roadmap"].add_roadmap_comment(self.current_roadmap_id, self.current_user.name, text)
            self._refresh_comments()

    def _selected_phase_id(self) -> int | None:
        # Fallback to first phase if no selection mechanism in PhaseListView yet
        phases = self.services["roadmap"].list_phases_with_tasks(self.current_roadmap_id) if self.current_roadmap_id else []
        return phases[0]["id"] if phases else None

    def _edit_phase(self, phase_id: int) -> None:
        modal = Modal(self, "Edit Phase")
        dialog = FormDialog(modal.body, title="")
        name_var = dialog.add_text("name", label="Phase Name")
        
        # Get current name
        roadmap = self.services["roadmap"].list_phases_with_tasks(self.current_roadmap_id)
        phase = next((p for p in roadmap if p["id"] == phase_id), None)
        if phase: name_var.set(phase["name"])

        def save() -> None:
            name = dialog.value("name")
            if name:
                self.services["roadmap"].update_phase(phase_id, name)
                modal.destroy()
                self._refresh_roadmap_tree()
        
        dialog.add_actions(save, confirm_text="Update")

    def _delete_phase(self, phase_id: int) -> None:
        if messagebox.askyesno("Confirm", "Delete this phase and all its tasks?"):
            self.services["roadmap"].delete_phase(phase_id)
            self._refresh_roadmap_tree()
            self._refresh_task_list()

    def _edit_task(self, task_id: int) -> None:
        task = self.services["task"].get_task(task_id)
        if not task: return
        
        modal = Modal(self, "Edit Task")
        form = TaskForm()
        form.render(modal.body)
        form.set_data({"title": task["title"], "weight": task["weight"]})

        def save() -> None:
            if not validate_or_warn(form.validate(), self.notifier): return
            data = form.get_data()
            self.services["roadmap"].update_task_details(task_id, data["title"], int(data["weight"]))
            modal.destroy()
            self._refresh_roadmap_tree()
            self._refresh_task_list()

        add_modal_actions(modal, save, confirm_text="Update")

    def _delete_task(self, task_id: int) -> None:
        if messagebox.askyesno("Confirm", "Delete this task?"):
            self.services["roadmap"].delete_task(task_id)
            self._refresh_roadmap_tree()
            self._refresh_task_list()

    def _show_charts(self) -> None:
        if not self.current_team_id: return
        team = self.services["team"].get_team(self.current_team_id)
        tasks = self.services["task"].list_tasks_for_roadmap(self.current_roadmap_id) if self.current_roadmap_id else []
        checkins = self.services["checkin"].list_checkins_for_team(self.current_team_id)
        show_reports_window(self, f"{team['name']} Charts", team["name"], tasks, checkins)
