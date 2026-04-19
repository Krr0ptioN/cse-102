from __future__ import annotations

import tkinter as tk

from libs.ui_kit.design_system import Typography
from libs.ui_kit.theme import palette


class RoleSelectFrame(tk.Frame):
    def __init__(self, master, on_select):
        colors = palette()
        super().__init__(master, bg=colors["bg"])
        self.on_select = on_select
        self._build()

    def _build(self) -> None:
        colors = palette()
        header = tk.Frame(self, bg=colors["bg"])
        header.pack(fill="x", pady=30)
        tk.Label(
            header,
            text="Project Lifecycle Engine",
            font=(Typography.primary_font_family(), 22, "bold"),
            bg=colors["bg"],
            fg=colors["text"],
        ).pack()
        tk.Label(
            header,
            text="Choose your workspace",
            font=(Typography.primary_font_family(), 11),
            bg=colors["bg"],
            fg=colors["muted"],
        ).pack(pady=6)

        cards = tk.Frame(self, bg=colors["bg"])
        cards.pack(pady=10)

        self._role_card(
            cards, "Teacher", "Manage classes, teams, and approvals", "teacher"
        ).grid(row=0, column=0, padx=16)
        self._role_card(
            cards, "Student", "Build roadmaps and update tasks", "student"
        ).grid(row=0, column=1, padx=16)

    def _role_card(self, master, title: str, desc: str, role: str) -> tk.Frame:
        colors = palette()
        frame = tk.Frame(
            master,
            bg=colors["panel"],
            highlightbackground=colors["border"],
            highlightthickness=1,
            padx=20,
            pady=16,
        )
        tk.Label(
            frame,
            text=title,
            font=(Typography.primary_font_family(), 14, "bold"),
            bg=colors["panel"],
        ).pack(anchor="w")
        tk.Label(
            frame,
            text=desc,
            font=(Typography.primary_font_family(), 10),
            bg=colors["panel"],
            fg=colors["muted"],
        ).pack(anchor="w", pady=6)
        tk.Button(
            frame,
            text=f"Open {title}",
            command=lambda: self.on_select(role),
        ).pack(anchor="w", pady=8)
        return frame
