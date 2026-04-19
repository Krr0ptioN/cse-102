from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

try:
    import customtkinter as ctk
except Exception:  # pragma: no cover - optional dependency
    ctk = None

from libs.ui_kit.design_system import palette
from ui.shared import apply_root_theme, ensure_local_db_path, resolve_root_class
from core.bootstrap import AppBootstrap
from core.services import AuthenticatedUser
from libs.logger import get_logger
from libs.ui_kit import SignInAuthCard, SignUpAuthCard
from ui.student.dashboard import StudentDashboard
from ui.teacher.dashboard import TeacherDashboard


BaseRoot = resolve_root_class()
log = get_logger("app.main")


class AppShell(BaseRoot):
    def __init__(self) -> None:
        super().__init__()
        log.banner("Application Startup")
        apply_root_theme(self)
        runtime = AppBootstrap(db_path_resolver=ensure_local_db_path).initialize()
        self.title(runtime.config.title)
        self.geometry(runtime.config.geometry)
        colors = palette()
        self.configure(bg=colors.bg)
        log.info("Using database at %s", runtime.config.db_path)

        self._services = runtime.services
        self._dataset_mode = runtime.dataset_mode
        self._auth_mode = "signin"
        self._colors = colors
        container_cls = ctk.CTkFrame if self._is_ctk() and ctk else tk.Frame
        container_kwargs = (
            {"fg_color": colors.bg} if self._is_ctk() and ctk else {"bg": colors.bg}
        )
        self.container = container_cls(self, **container_kwargs)
        self.container.pack(fill="both", expand=True)

        self._show_login()
        log.success("App shell initialized")

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

        auth_card_cls = SignUpAuthCard if sign_up_mode else SignInAuthCard
        auth_card = auth_card_cls(
            frame,
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
        log.success("Session started for %s (%s)", user.email, user.role)
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
        log.info("Session cleared")
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
