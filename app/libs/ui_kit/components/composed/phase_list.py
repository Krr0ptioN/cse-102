from __future__ import annotations

import tkinter as tk
from libs.ui_kit.theme import palette
from libs.ui_kit.design_system import Typography
from ..primitives import ScrollableFrame, Badge, Label, Button
from .task_list import TaskRow


class PhaseRow(tk.Frame):
    """A collapsible phase header with a list of tasks."""
    
    def __init__(self, master, phase_id: int, name: str, tasks: list[dict], on_task_select=None, on_edit_phase=None, on_delete_phase=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["surface"])
        super().__init__(master, bg=bg)
        self.phase_id = phase_id
        self.is_open = tk.BooleanVar(value=True)
        self.on_task_select = on_task_select
        self.on_edit_phase = on_edit_phase
        self.on_delete_phase = on_delete_phase

        # Header
        self.header = tk.Frame(self, bg=colors["panel"], padx=12, pady=8)
        self.header.pack(fill="x")
        
        self.toggle_btn = tk.Label(
            self.header, 
            text="▼", 
            font=(Typography.primary_font_family(), 10),
            bg=colors["panel"],
            fg=colors["muted"],
            cursor="hand2"
        )
        self.toggle_btn.pack(side="left", padx=(0, 8))
        self.toggle_btn.bind("<Button-1>", lambda _: self.toggle())

        tk.Label(
            self.header,
            text=name.upper(),
            font=(Typography.primary_font_family(), 9, "bold"),
            bg=colors["panel"],
            fg=colors["text"],
            anchor="w",
        ).pack(side="left")
        
        # Actions for teachers/principals
        if on_delete_phase:
             btn = tk.Label(self.header, text="Delete", font=(Typography.primary_font_family(), 8), bg=colors["panel"], fg=colors["danger"], cursor="hand2")
             btn.pack(side="right", padx=4)
             btn.bind("<Button-1>", lambda _: on_delete_phase(self.phase_id))
        
        if on_edit_phase:
             btn = tk.Label(self.header, text="Edit", font=(Typography.primary_font_family(), 8), bg=colors["panel"], fg=colors["muted"], cursor="hand2")
             btn.pack(side="right", padx=4)
             btn.bind("<Button-1>", lambda _: on_edit_phase(self.phase_id))

        # Task Container
        self.task_container = tk.Frame(self, bg=bg)
        self.task_container.pack(fill="x")
        
        self._render_tasks(tasks)

    def toggle(self) -> None:
        if self.is_open.get():
            self.task_container.pack_forget()
            self.toggle_btn.config(text="▶")
            self.is_open.set(False)
        else:
            self.task_container.pack(fill="x")
            self.toggle_btn.config(text="▼")
            self.is_open.set(True)

    def _render_tasks(self, tasks: list[dict]) -> None:
        for t in tasks:
            row = TaskRow(
                self.task_container, 
                t["id"], 
                t["title"], 
                t["status"], 
                t["weight"],
                on_select=self.on_task_select
            )
            row.pack(fill="x")


class PhaseListView(tk.Frame):
    def __init__(self, master, on_task_select=None, on_edit_phase=None, on_delete_phase=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["bg"])
        super().__init__(master, bg=bg)
        self.on_task_select = on_task_select
        self.on_edit_phase = on_edit_phase
        self.on_delete_phase = on_delete_phase

        self.scroll_frame = ScrollableFrame(self, bg=bg)
        self.scroll_frame.pack(fill="both", expand=True)

    def set_phases(self, phases: list[dict]) -> None:
        """phases: list of dicts with {id, name, tasks: []}"""
        self.scroll_frame.clear()
        for p in phases:
            row = PhaseRow(
                self.scroll_frame.scrollable_content,
                p["id"],
                p["name"],
                p.get("tasks", []),
                on_task_select=self.on_task_select,
                on_edit_phase=self.on_edit_phase,
                on_delete_phase=self.on_delete_phase
            )
            row.pack(fill="x", pady=(0, 12))
