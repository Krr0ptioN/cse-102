from __future__ import annotations

import tkinter as tk
from pathlib import Path

from app.ui.teacher_dashboard import TeacherDashboard
from app.ui.student_dashboard import StudentDashboard

from app.db.connector import DBConnector
from app.db.schema import init_db
from app.services.factory import ServiceFactory
from app.ui.theme import apply_theme
from app.ui.role_select import RoleSelectFrame


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Project Lifecycle Engine")
        self.geometry("1000x700")
        apply_theme(self)
        self.db_path = str(Path(__file__).resolve().parents[1] / "app.db")
        init_db(self.db_path)
        self.db = DBConnector(self.db_path)
        self.services = ServiceFactory(self.db)

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames: dict[str, tk.Frame] = {}
        self._show_role_select()

    def _show_role_select(self) -> None:
        self._clear_frames()
        frame = RoleSelectFrame(self.container, self._handle_role)
        self.frames["role_select"] = frame
        frame.pack(fill="both", expand=True)

    def _handle_role(self, role: str) -> None:
        if role == "teacher":
            self._show_teacher()
        elif role == "student":
            self._show_student()

    def _show_teacher(self) -> None:

        self._clear_frames()
        frame = TeacherDashboard(
            self.container,
            self.services.class_service,
            self.services.checkin_service,
            self.services.team_service,
            self.services.roadmap_service,
            self.services.task_service,
            self._show_role_select,
        )
        self.frames["teacher"] = frame
        frame.pack(fill="both", expand=True)

    def _show_student(self) -> None:

        self._clear_frames()
        frame = StudentDashboard(
            self.container,
            self.services.class_service,
            self.services.checkin_service,
            self.services.team_service,
            self.services.roadmap_service,
            self.services.task_service,
            self._show_role_select,
        )
        self.frames["student"] = frame
        frame.pack(fill="both", expand=True)

    def _clear_frames(self) -> None:
        for child in self.container.winfo_children():
            child.destroy()
        self.frames.clear()


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
