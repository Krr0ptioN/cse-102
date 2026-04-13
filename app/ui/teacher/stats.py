from __future__ import annotations

import tkinter as tk

from app.libs.ui_kit.components import StatCard


class TeacherStatsRow(tk.Frame):
    def __init__(self, master) -> None:
        super().__init__(master)
        self.grid_columnconfigure((0, 1, 2), weight=1)

        self.students = StatCard(self, "Students", "0")
        self.students.grid(row=0, column=0, padx=8, sticky="ew")
        self.teams = StatCard(self, "Teams", "0")
        self.teams.grid(row=0, column=1, padx=8, sticky="ew")
        self.roadmaps = StatCard(self, "Roadmaps", "0")
        self.roadmaps.grid(row=0, column=2, padx=8, sticky="ew")

    def set_counts(self, students: int, teams: int, roadmaps: int) -> None:
        self.students.set_value(str(students))
        self.teams.set_value(str(teams))
        self.roadmaps.set_value(str(roadmaps))
