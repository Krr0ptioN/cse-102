from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.services.team_service import list_all_teams


class StudentDashboard(tk.Frame):
    def __init__(self, master, db_path: str, on_back) -> None:
        super().__init__(master)
        self.db_path = db_path
        self.on_back = on_back
        self._build()
        self._refresh_teams()

    def _build(self) -> None:
        header = tk.Frame(self)
        header.pack(fill="x", pady=10)
        tk.Button(header, text="Back", command=self.on_back).pack(side="left", padx=10)
        tk.Label(header, text="Student Dashboard", font=("Helvetica", 16, "bold")).pack(
            side="left", padx=10
        )

        selector = tk.Frame(self)
        selector.pack(fill="x", pady=5)
        tk.Label(selector, text="Team").pack(side="left", padx=5)
        self.team_select = ttk.Combobox(selector, state="readonly")
        self.team_select.pack(side="left", padx=5)

        content = tk.Frame(self)
        content.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_roadmap_panel(content)
        self._build_task_panel(content)

    def _build_roadmap_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Roadmap Builder")
        frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.roadmap_tree = ttk.Treeview(frame, columns=("type", "weight"), show="tree")
        self.roadmap_tree.pack(fill="both", expand=True, padx=5, pady=5)

    def _build_task_panel(self, parent: tk.Frame) -> None:
        frame = tk.LabelFrame(parent, text="Tasks")
        frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        self.task_list = tk.Listbox(frame)
        self.task_list.pack(fill="both", expand=True, padx=5, pady=5)

        self.update_text = tk.Text(frame, height=5)
        self.update_text.pack(fill="x", padx=5, pady=5)

        tk.Button(frame, text="Add Update").pack(pady=5)

    def _refresh_teams(self) -> None:
        teams = list_all_teams(self.db_path)
        choices = [f"{team['id']} {team['name']}" for team in teams]
        self.team_select["values"] = choices
        if choices:
            self.team_select.current(0)
