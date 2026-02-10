from __future__ import annotations

import tkinter as tk
from pathlib import Path

from app.db.schema import init_db
from app.services.class import ClassService
from app.services.roadmap import RoadmapService
from app.services.task import TaskService
from app.services.team import TeamService
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
        self.class_service = ClassService(self.db_path)
        self.team_service = TeamService(self.db_path)
        self.roadmap_service = RoadmapService(self.db_path)
        self.task_service = TaskService(self.db_path)

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
        from app.ui.teacher_dashboard import TeacherDashboard

        self._clear_frames()
        frame = TeacherDashboard(
            self.container,
            self.class_service,
            self.team_service,
            self.roadmap_service,
            self.task_service,
            self._show_role_select,
        )
        self.frames["teacher"] = frame
        frame.pack(fill="both", expand=True)

    def _show_student(self) -> None:
        from app.ui.student_dashboard import StudentDashboard

        self._clear_frames()
        frame = StudentDashboard(
            self.container,
            self.team_service,
            self.roadmap_service,
            self.task_service,
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
