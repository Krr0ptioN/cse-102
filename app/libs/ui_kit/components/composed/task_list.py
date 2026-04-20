from __future__ import annotations

import tkinter as tk
from ...theme import palette
from ...design_system import Typography
from ..primitives import ScrollableFrame, Badge


class TaskRow(tk.Frame):
    def __init__(self, master, task_id: int, title: str, status: str, weight: int, on_select=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["surface"])
        super().__init__(master, bg=bg, cursor="hand2")
        self.task_id = task_id
        self.on_select = on_select

        # Status dot/badge
        status_colors = {
            "Todo": "#64748B",
            "In Progress": "#3B82F6",
            "Done": "#10B981",
            "Blocked": "#EF4444",
        }
        dot_color = status_colors.get(status, "#64748B")

        self.dot = tk.Frame(self, width=8, height=8, bg=dot_color)
        self.dot.pack(side="left", padx=(12, 12))
        self.dot.pack_propagate(False)

        tk.Label(
            self,
            text=f"T-{task_id}",
            font=(Typography.primary_font_family(), 9),
            bg=bg,
            fg=colors["muted"],
            width=5,
            anchor="w",
        ).pack(side="left")

        self.title_label = tk.Label(
            self,
            text=title,
            font=(Typography.primary_font_family(), 10),
            bg=bg,
            fg=colors["text"],
            anchor="w",
        )
        self.title_label.pack(side="left", fill="x", expand=True, padx=8)

        # Weight badge
        Badge(self, text=f"w{weight}", variant="outline").pack(side="right", padx=12)

        # Bottom border
        tk.Frame(self, height=1, bg=colors["border"]).place(relx=0, rely=1, relwidth=1, anchor="sw")

        # Events
        for widget in (self, self.title_label, self.dot):
            widget.bind("<Button-1>", self._handle_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _handle_click(self, _event) -> None:
        if self.on_select:
            self.on_select(self.task_id)

    def _on_enter(self, _event) -> None:
        colors = palette()
        self.configure(bg=colors["panel"])
        self.title_label.configure(bg=colors["panel"])

    def _on_leave(self, _event) -> None:
        colors = palette()
        self.configure(bg=colors["surface"])
        self.title_label.configure(bg=colors["surface"])


class TaskListView(tk.Frame):
    def __init__(self, master, on_task_select=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["bg"])
        super().__init__(master, bg=bg)
        self.on_task_select = on_task_select

        self.scroll_frame = ScrollableFrame(self, bg=bg)
        self.scroll_frame.pack(fill="both", expand=True)

    def set_tasks(self, tasks: list[tuple[int, str, str, int]]) -> None:
        """tasks: list of (id, title, status, weight)"""
        self.scroll_frame.clear()
        for tid, title, status, weight in tasks:
            row = TaskRow(self.scroll_frame.scrollable_content, tid, title, status, weight, on_select=self.on_task_select)
            row.pack(fill="x", pady=0, ipady=8)
