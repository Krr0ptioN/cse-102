from __future__ import annotations

import tkinter as tk

from app.ui.components import DetailsDrawer


class StudentDrawer(DetailsDrawer):
    def __init__(self, master) -> None:
        super().__init__(master, "Details")

    def render_team_header(self, team_id: int, team_name: str, principal: str) -> None:
        tk.Label(self.body, text=f"Team #{team_id}").pack(anchor="w")
        tk.Label(self.body, text=f"Name: {team_name}").pack(anchor="w")
        tk.Label(self.body, text=f"Principal: {principal}").pack(anchor="w")
        tk.Frame(self.body, height=1, bg="#CBD5E1").pack(fill="x", pady=6)
