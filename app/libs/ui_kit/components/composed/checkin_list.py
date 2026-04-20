from __future__ import annotations

import tkinter as tk
from ...theme import palette
from ...design_system import Typography
from ..primitives import ScrollableFrame, Badge, Label
from .utils import format_timestamp


class CheckinRow(tk.Frame):
    def __init__(self, master, checkin_id: int, week: str, status: str, progress: str, submitted_at: str, on_select=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["surface"])
        super().__init__(master, bg=bg, cursor="hand2")
        self.checkin_id = checkin_id
        self.on_select = on_select

        # Left border status indicator
        status_colors = {
            "Approved": "#10B981", # Green
            "Submitted": "#3B82F6", # Blue
            "Draft": "#64748B",     # Slate
            "Changes Requested": "#EF4444", # Red
        }

        # Determine Health Color (based on status or status string)
        # In a real app, we'd check a 'health' field or logic
        health_color = status_colors.get(status, "#64748B")
        if "risk" in status.lower() or "blocked" in status.lower():
            health_color = "#EF4444"
        elif "track" in status.lower():
            health_color = "#10B981"

        self.accent_bar = tk.Frame(self, width=6, bg=health_color)
        self.accent_bar.pack(side="left", fill="y")
        content = tk.Frame(self, bg=bg, padx=12, pady=10)
        content.pack(side="left", fill="both", expand=True)

        header = tk.Frame(content, bg=bg)
        header.pack(fill="x")

        tk.Label(
            header,
            text=f"Check-in #{checkin_id}",
            font=(Typography.primary_font_family(), 9, "bold"),
            bg=bg,
            fg=colors["muted"],
        ).pack(side="left")

        tk.Label(
            header,
            text=format_timestamp(submitted_at),
            font=(Typography.primary_font_family(), 8),
            bg=bg,
            fg=colors["muted"],
        ).pack(side="right")


        mid = tk.Frame(content, bg=bg)
        mid.pack(fill="x", pady=(4, 4))

        tk.Label(
            mid,
            text=week,
            font=(Typography.primary_font_family(), 11, "bold"),
            bg=bg,
            fg=colors["text"],
        ).pack(side="left")

        # Progress bar
        try:
            percent = int(progress.replace("%", ""))
        except:
            percent = 0
            
        progress_container = tk.Frame(content, bg=colors["border"], height=4)
        progress_container.pack(fill="x", pady=(4, 0))
        progress_container.pack_propagate(False)
        
        tk.Frame(progress_container, bg="#10B981", width=percent*2).pack(side="left", fill="y")

        # Footer info
        footer = tk.Frame(content, bg=bg)
        footer.pack(fill="x", pady=(6, 0))
        
        Badge(footer, text=status, variant="outline").pack(side="left")
        tk.Label(
            footer,
            text=f"Progress: {progress}",
            font=(Typography.primary_font_family(), 9),
            bg=bg,
            fg=colors["muted"],
        ).pack(side="right")

        # Events
        for widget in (self, content, header, mid, footer):
            widget.bind("<Button-1>", self._handle_click)
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)

    def _handle_click(self, _event) -> None:
        if self.on_select:
            self.on_select(self.checkin_id)

    def _on_enter(self, _event) -> None:
        colors = palette()
        self.configure(bg=colors["panel"])
        for child in self.winfo_children():
            if isinstance(child, tk.Frame) and child != self.accent_bar:
                child.configure(bg=colors["panel"])
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=colors["panel"])

    def _on_leave(self, _event) -> None:
        colors = palette()
        self.configure(bg=colors["surface"])
        for child in self.winfo_children():
             if isinstance(child, tk.Frame) and child != self.accent_bar:
                child.configure(bg=colors["surface"])
                for sub in child.winfo_children():
                    if isinstance(sub, tk.Label):
                        sub.configure(bg=colors["surface"])


class CheckinListView(tk.Frame):
    def __init__(self, master, on_checkin_select=None, **kwargs) -> None:
        colors = palette()
        bg = kwargs.get("bg", colors["bg"])
        super().__init__(master, bg=bg)
        self.on_checkin_select = on_checkin_select

        self.scroll_frame = ScrollableFrame(self, bg=bg)
        self.scroll_frame.pack(fill="both", expand=True)

    def set_checkins(self, checkins: list[tuple]) -> None:
        """checkins: list of (id, week, status, progress, submitted_at)"""
        self.scroll_frame.clear()
        for c in checkins:
            row = CheckinRow(
                self.scroll_frame.scrollable_content, 
                c[0], c[1], c[2], c[3], c[4],
                on_select=self.on_checkin_select
            )
            row.pack(fill="x", pady=4, padx=8)
