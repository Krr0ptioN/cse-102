from __future__ import annotations

import tkinter as tk
from libs.ui_kit.theme import palette
from libs.ui_kit.design_system import Typography
from ..primitives import ScrollableFrame, Badge, Label


class TeamRow(tk.Frame):
    def __init__(self, master, team_id: int, name: str, principal: str, on_select=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["surface"])
        super().__init__(master, bg=bg, cursor="hand2")
        self.team_id = team_id
        self.on_select = on_select

        content = tk.Frame(self, bg=bg, padx=16, pady=12)
        content.pack(fill="both", expand=True)

        tk.Label(
            content,
            text=f"#{team_id}",
            font=(Typography.primary_font_family(), 9),
            bg=bg,
            fg=colors["muted"],
            width=4,
            anchor="w",
        ).pack(side="left")

        self.name_label = tk.Label(
            content,
            text=name,
            font=(Typography.primary_font_family(), 11, "bold"),
            bg=bg,
            fg=colors["text"],
            anchor="w",
        )
        self.name_label.pack(side="left", fill="x", expand=True, padx=8)

        if principal and principal != "-":
            p_frame = tk.Frame(content, bg=bg)
            p_frame.pack(side="right")
            tk.Label(p_frame, text="Principal: ", font=(Typography.primary_font_family(), 9), bg=bg, fg=colors["muted"]).pack(side="left")
            Badge(p_frame, text=principal, variant="default").pack(side="left")

        # Bottom border
        tk.Frame(self, height=1, bg=colors["border"]).place(relx=0, rely=1, relwidth=1, anchor="sw")

        # Events
        for widget in (self, content, self.name_label):
            widget.bind("<Button-1>", self._handle_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _handle_click(self, _event) -> None:
        if self.on_select:
            self.on_select(self.team_id)

    def _on_enter(self, _event) -> None:
        colors = palette()
        self.configure(bg=colors["panel"])
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors["panel"])
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=colors["panel"])

    def _on_leave(self, _event) -> None:
        colors = palette()
        self.configure(bg=colors["surface"])
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.configure(bg=colors["surface"])
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=colors["surface"])


class TeamListView(tk.Frame):
    def __init__(self, master, on_team_select=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["bg"])
        super().__init__(master, bg=bg)
        self.on_team_select = on_team_select

        self.scroll_frame = ScrollableFrame(self, bg=bg)
        self.scroll_frame.pack(fill="both", expand=True)

    def set_teams(self, teams: list[tuple[int, str, str]]) -> None:
        """teams: list of (id, name, principal)"""
        self.scroll_frame.clear()
        for tid, name, principal in teams:
            row = TeamRow(self.scroll_frame.scrollable_content, tid, name, principal, on_select=self.on_team_select)
            row.pack(fill="x", pady=0)
