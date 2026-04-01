from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from app.ui.teacher import StudentRosterSection


class TeacherStudentsPage(tk.Frame):
    title = "Students"

    def __init__(self, master, services: dict) -> None:
        colors_bg = master["bg"] if isinstance(master, tk.BaseWidget) else None
        super().__init__(master, bg=colors_bg)
        self.services = services
        self._build()
        self._refresh_students()

    def _build(self) -> None:
        self.student_section = StudentRosterSection(
            self,
            self._add_student,
            self._edit_student,
            self._delete_student,
            self._show_student_details,
        )
        self.student_section.pack(fill="both", expand=True, padx=8, pady=8)

    def _refresh_students(self) -> None:
        students = self.services["class"].list_users(role="student")
        rows = [(s["id"], s["name"], s["email"]) for s in students]
        self.student_section.set_rows(rows)

    def _add_student(self, data: dict) -> None:
        self.services["class"].create_user(data["name"], data["email"], "student")
        self._refresh_students()

    def _edit_student(self, student_id: int, data: dict) -> None:
        self.services["class"].update_user(student_id, data["name"], data["email"])
        self._refresh_students()

    def _delete_student(self, student_id: int) -> None:
        self.services["class"].delete_user(student_id)
        self._refresh_students()

    def _show_student_details(self) -> None:
        # handled by the drawer in dashboard; no-op here
        return
