from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from libs.ui_kit import CheckinListView, CommentThread, Button, Label, Section, palette
from ui.shared.page import Page


class TeacherCheckinsPage(Page):
    title = "Check-ins"
    route = "checkins"

    def on_mount(self) -> None:
        self.list_view = CheckinListView(
            self, on_checkin_select=self._on_checkin_selected
        )
        self.list_view.pack(fill="both", expand=True, padx=12, pady=12)

    def on_show(self) -> None:
        self._refresh_checkins()

    def _refresh_checkins(self) -> None:
        class_id = self.dashboard.class_id
        if not class_id:
            self.list_view.set_checkins([])
            return
            
        checkins = self.dashboard.services["checkin"].list_checkins_for_class(class_id)
        rows = [
            (
                c["id"],
                f"[{c['team']}] {c['week_start']} → {c['week_end']}",
                c["status"],
                f"{c['percent']}%",
                c["submitted_at"],
            )
            for c in checkins
        ]
        self.list_view.set_checkins(rows)

    def _on_checkin_selected(self, checkin_id: int) -> None:
        self.dashboard.slide_over.clear()
        self.dashboard.slide_over.config(width=340) # Wider for checkin details
        
        chk = self.dashboard.services["checkin"].get_checkin(checkin_id)
        if not chk:
            return

        body = self.dashboard.slide_over.body
        bg = body["bg"]

        # Header info
        Label(body, text=f"Check-in #{checkin_id}", weight="bold", size="lg").pack(anchor="w", pady=(0, 4))
        Label(body, text=f"Team: {chk['team_name']}", variant="muted").pack(anchor="w")
        Label(body, text=f"Period: {chk['week_start']} → {chk['week_end']}", variant="muted").pack(anchor="w")
        
        # Stats summary
        stats_frame = tk.Frame(body, bg=bg, pady=12)
        stats_frame.pack(fill="x")
        
        progress_val = chk.get('metrics_percent', chk.get('percent', 0))
        Label(stats_frame, text=f"Completion: {progress_val}%", weight="bold").pack(anchor="w")
        
        # Details sections
        colors = self.dashboard.slide_over.palette if hasattr(self.dashboard.slide_over, "palette") else palette()
        for title, key in [("Wins", "wins"), ("Risks", "risks"), ("Next Goals", "next_goal")]:
            Section(body, title, subtitle=None).pack(fill="x", pady=4)
            tk.Label(
                body, 
                text=chk.get(key, "None"), 
                bg=bg, 
                fg=colors["text"],
                wraplength=300,
                justify="left",
                anchor="w"
            ).pack(fill="x", padx=4, pady=(0, 8))

        # Comment Thread
        comment_section = Section(body, "Feedback & Discussion")
        comment_section.pack(fill="both", expand=True, pady=(12, 0))
        
        thread = CommentThread(comment_section.body, on_send=lambda txt: self._add_comment(checkin_id, txt))
        thread.pack(fill="both", expand=True)
        
        comments = self.dashboard.services["checkin"].list_checkin_comments(checkin_id)
        thread.set_comments([(c["author"], c["text"], c["created_at"]) for c in comments])

        # Action buttons
        if chk["status"] == "Submitted":
            Button(
                self.dashboard.slide_over.actions, 
                text="Approve Check-in", 
                command=lambda: self._approve_checkin(checkin_id)
            ).pack(fill="x", pady=4)

    def _add_comment(self, checkin_id: int, text: str) -> None:
        self.dashboard.services["checkin"].add_checkin_comment(
            checkin_id, "Teacher", text, "comment"
        )
        self._on_checkin_selected(checkin_id) # Refresh drawer

    def _approve_checkin(self, checkin_id: int) -> None:
        if hasattr(self.dashboard.services["checkin"], "approve_checkin"):
            self.dashboard.services["checkin"].approve_checkin(checkin_id)
            self._refresh_checkins()
            self._on_checkin_selected(checkin_id)
