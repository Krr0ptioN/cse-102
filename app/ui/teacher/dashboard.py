from __future__ import annotations

from tkinter import messagebox

from core.services import (
    AuthenticatedUser,
    CheckinService,
    ClassService,
    RoadmapService,
    TaskService,
    TeamService,
)
from libs.ui_kit import FormDialog
from ui.shared import (
    show_reports_window,
    DashboardBase
)
from .pages import (
    TeacherCheckinsPage,
    TeacherClassesPage,
    TeacherHomePage,
    TeacherRoadmapsPage,
    TeacherStudentsPage,
    TeacherTeamsPage,
)


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
        self.current_user = current_user
        self.demo_mode = demo_mode

        self.class_service = class_service
        self.checkin_service = checkin_service
        self.team_service = team_service
        self.roadmap_service = roadmap_service
        self.task_service = task_service

        self._services = {
            "class": class_service,
            "checkin": checkin_service,
            "team": team_service,
            "roadmap": roadmap_service,
            "task": task_service,
        }

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
        self._current_page: str | None = None
        self._navigate("dashboard")
        self.log.success("Teacher dashboard ready for %s", self.current_user.email)

    def _autoselect_class(self) -> None:
        classes = self.class_service.list_classes(
            owner_user_id=self.current_user.id
        )
        if not classes:
            self.class_id = None
            return
        first = classes[0]
        self.class_id = first["id"] if isinstance(first, dict) else first[0]

    def build_layout(self) -> None:
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
        if page is None:
            return
        self.swap_content(page)
        self._current_page = route
        self.set_active_nav(route)
        self.log.info("Teacher view -> %s", route)

    def _create_page(
        self, route: str
    ) -> (
        TeacherHomePage
        | TeacherClassesPage
        | TeacherStudentsPage
        | TeacherTeamsPage
        | TeacherRoadmapsPage
        | TeacherCheckinsPage
        | None
    ):
        return {
            "dashboard": TeacherHomePage(
                self.shell.content,
                self._services,
                self.class_id),
            "classes": TeacherClassesPage(
                self.shell.content,
                self._services,
                owner_user_id=self.current_user.id,
                current_class_id=self.class_id,
                on_select_class=self._set_active_class,
            ),
            "students": TeacherStudentsPage(
                self.shell.content,
                self._services
            ),
            "teams": TeacherTeamsPage(
                self.shell.content,
                self._services,
                self.class_id
            ),
            "roadmaps": TeacherRoadmapsPage(
                self.shell.content,
                self._services,
                self.class_id
            ),
            "checkins": TeacherCheckinsPage(
                self.shell.content,
                self._services,
                self.class_id
            ),
        }.get(route, None)

    def _set_active_class(self, class_id: int) -> None:
        self.class_id = class_id
        self.log.info("Active class selected: %s", class_id)

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
        options: list[str] = []
        team_by_option: dict[str, dict] = {}
        for team in teams:
            principal = team.get("principal_name") or "-"
            label = f"#{team['id']} · {team['name']} · {principal}"
            options.append(label)
            team_by_option[label] = team

        dialog = FormDialog(
            self,
            title="Select Team",
            subtitle="Choose a team to open report charts.",
        )
        dialog.add_select("team", label="Team", values=options, width=42)

        def choose_and_open() -> None:
            selection = dialog.value("team")
            team = team_by_option.get(selection)
            if not team:
                messagebox.showwarning("No team", "Select a team to view reports.")
                return
            dialog.destroy()
            self._open_team_reports(team)

        dialog.add_actions(choose_and_open, confirm_text="Open")

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
