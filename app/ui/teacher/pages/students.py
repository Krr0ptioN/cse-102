from __future__ import annotations

import tkinter as tk

from ui.teacher import StudentRosterSection
from ui.shared.page import Page


class TeacherStudentsPage(Page):
    title = "Students"
    route = "students"

    def __init__(self, dashboard) -> None:
        super().__init__(dashboard)

    def on_mount(self) -> None:
        self.student_section = StudentRosterSection(
            self,
            self._add_student,
            self._edit_student,
            self._delete_student,
            self._show_student_details,
        )
        self.student_section.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self._refresh_students()

    def _refresh_students(self) -> None:
        students = self.dashboard.services["class"].list_users(role="student")
        rows = [(s["id"], s["name"], s["email"]) for s in students]
        self.student_section.set_rows(rows)

    def _add_student(self, data: dict) -> None:
        self.dashboard.services["class"].create_user(data["name"], data["email"], "student")
        self._refresh_students()

    def _edit_student(self, student_id: int, data: dict) -> None:
        self.dashboard.services["class"].update_user(student_id, data["name"], data["email"])
        self._refresh_students()

    def _delete_student(self, student_id: int) -> None:
        self.dashboard.services["class"].delete_user(student_id)
        self._refresh_students()

    def _show_student_details(self) -> None:
        # handled by the drawer in dashboard; no-op here
        return
