from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional dependency
    ctk = None

from app.design_system.tokens import palette
from app.db.connector import DBConnector
from app.db.schema import init_db
from app.services.auth import AuthenticatedUser
from app.services.factory import ServiceFactory
from app.ui.components.composed import AuthCard
from app.ui.root_factory import resolve_root_class, apply_root_theme
from app.ui.student_dashboard import StudentDashboard
from app.ui.teacher_dashboard import TeacherDashboard


BaseRoot = resolve_root_class()


class AppShell(BaseRoot):
    def __init__(self) -> None:
        super().__init__()
        apply_root_theme(self)
        self.title("Project Lifecycle Engine")
        self.geometry("1100x740")
        colors = palette()
        self.configure(bg=colors.bg)

        db_path = "app.db"
        init_db(db_path)
        db = DBConnector(db_path)
        services = ServiceFactory(db)

        self._services = services
        self._dataset_mode = self._services.app_state_service.get_dataset_mode()
        self._auth_mode = "signin"
        self._colors = colors
        container_cls = ctk.CTkFrame if self._is_ctk() and ctk else tk.Frame
        container_kwargs = (
            {"fg_color": colors.bg} if self._is_ctk() and ctk else {"bg": colors.bg}
        )
        self.container = container_cls(self, **container_kwargs)
        self.container.pack(fill="both", expand=True)

        self._show_login()

    # ----- Navigation -------------------------------------------------
    def _clear_container(self) -> None:
        for child in list(self.container.winfo_children()):
            child.destroy()

    def _is_ctk(self) -> bool:
        return ctk is not None and isinstance(self, ctk.CTk)

    def _show_login(self) -> None:
        self._clear_container()
        colors = self._colors
        sign_up_mode = self._auth_mode == "signup"
        frame_cls = ctk.CTkFrame if self._is_ctk() and ctk else tk.Frame
        frame_kwargs = (
            {"fg_color": colors.bg} if self._is_ctk() and ctk else {"bg": colors.bg}
        )
        frame = frame_cls(self.container, **frame_kwargs)
        frame.pack(fill="both", expand=True)

        auth_card = AuthCard(
            frame,
            sign_up_mode=sign_up_mode,
            on_submit=self._submit_auth,
            on_switch=lambda: self._switch_auth_mode(
                "signin" if sign_up_mode else "signup"
            ),
        )
        auth_card.place_center()

    def _submit_auth(self, data: dict[str, str]) -> None:
        if self._auth_mode == "signup":
            self._attempt_sign_up(
                data.get("name", ""),
                data.get("email", ""),
                data.get("password", ""),
                data.get("role", "student"),
            )
            return
        self._attempt_sign_in(
            data.get("email", ""),
            data.get("password", ""),
        )

    def _switch_auth_mode(self, mode: str) -> None:
        self._auth_mode = "signup" if mode == "signup" else "signin"
        self._show_login()

    def _attempt_sign_in(self, email: str, password: str) -> None:
        try:
            user = self._services.auth_service.sign_in(email, password)
        except ValueError as exc:
            messagebox.showerror("Sign In Failed", str(exc))
            return
        self._start_session(user)

    def _attempt_sign_up(self, name: str, email: str, password: str, role: str) -> None:
        try:
            user = self._services.auth_service.sign_up(name, email, password, role)
        except ValueError as exc:
            messagebox.showerror("Sign Up Failed", str(exc))
            return
        self._start_session(user)

    def _start_session(self, user: AuthenticatedUser) -> None:
        self._services.session_service.start(user)
        if user.role == "teacher":
            self._load_teacher()
            return
        if user.role == "student":
            self._load_student()
            return
        messagebox.showerror("Invalid Role", f"Unsupported role: {user.role}")
        self._services.session_service.clear()
        self._show_login()

    def _logout(self) -> None:
        self._services.session_service.clear()
        self._show_login()

    def _load_teacher(self) -> None:
        try:
            current_user = self._services.session_service.require_user()
        except ValueError:
            self._show_login()
            return
        if current_user.role != "teacher":
            messagebox.showerror("Access denied", "Teacher account required")
            self._show_login()
            return
        self._clear_container()
        teacher = TeacherDashboard(
            self.container,
            self._services.class_service,
            self._services.checkin_service,
            self._services.team_service,
            self._services.roadmap_service,
            self._services.task_service,
            current_user=current_user,
            demo_mode=self._dataset_mode == "mock",
            on_back=self._logout,
        )
        teacher.pack(fill="both", expand=True)

    def _load_student(self) -> None:
        try:
            current_user = self._services.session_service.require_user()
        except ValueError:
            self._show_login()
            return
        if current_user.role != "student":
            messagebox.showerror("Access denied", "Student account required")
            self._show_login()
            return
        self._clear_container()
        student = StudentDashboard(
            self.container,
            self._services.class_service,
            self._services.checkin_service,
            self._services.team_service,
            self._services.roadmap_service,
            self._services.task_service,
            current_user=current_user,
            demo_mode=self._dataset_mode == "mock",
            on_back=self._logout,
        )
        student.pack(fill="both", expand=True)


def main() -> None:
    app = AppShell()
    app.mainloop()


if __name__ == "__main__":
    main()
