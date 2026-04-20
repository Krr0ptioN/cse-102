from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from libs.ui_kit import CheckinListView, CommentThread, Label, Section, Button
from ui.student.pages.base import StudentSectionPage


class StudentCheckinsPage(StudentSectionPage):
    title = "Check-ins"
    route = "checkins"
    subtitle = "Weekly status reports and progress metrics."

    def on_mount(self) -> None:
        super().on_mount()
        self.list_view = CheckinListView(self.body, on_checkin_select=self._on_checkin_selected)
        self.list_view.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self._refresh_checkins()

    def _refresh_checkins(self) -> None:
        team_id = self.dashboard.current_team_id
        if not team_id:
            self.list_view.set_checkins([])
            return
            
        checkins = self.dashboard.services["checkin"].list_checkins_for_team(team_id)
        rows = [
            (
                c["id"],
                f"{c['week_start']} → {c['week_end']}",
                c["status"],
                f"{c.get('metrics_percent', c.get('percent', 0))}%",
                c["submitted_at"],
            )
            for c in checkins
        ]
        self.list_view.set_checkins(rows)

    def _on_checkin_selected(self, checkin_id: int) -> None:
        self.dashboard.slide_over.clear()
        
        chk = self.dashboard.services["checkin"].get_checkin(checkin_id)
        if not chk:
            return

        body = self.dashboard.slide_over.body
        bg = body["bg"]

        # Header
        Label(body, text=f"Check-in #{checkin_id}", weight="bold", size="lg").pack(anchor="w", pady=(0, 4))
        Label(body, text=f"Week: {chk['week_start']} → {chk['week_end']}", variant="muted").pack(anchor="w")
        
        # Details
        for title, key in [("Wins", "wins"), ("Risks", "risks"), ("Next Goal", "next_goal")]:
            Section(body, title, subtitle=None).pack(fill="x", pady=4)
            tk.Label(
                body, 
                text=chk.get(key, "None"), 
                bg=bg, 
                fg=palette()["text"],
                wraplength=280,
                justify="left",
                anchor="w"
            ).pack(fill="x", padx=4, pady=(0, 8))

        # Comments
        comment_sec = Section(body, "Teacher Feedback")
        comment_sec.pack(fill="both", expand=True, pady=(12, 0))
        
        thread = CommentThread(comment_sec.body, on_send=lambda txt: self._add_comment(checkin_id, txt))
        thread.pack(fill="both", expand=True)
        
        comments = self.dashboard.services["checkin"].list_checkin_comments(checkin_id)
        thread.set_comments([(c["author"], c["text"], c["created_at"]) for c in comments])

    def _add_comment(self, checkin_id: int, text: str) -> None:
        self.dashboard.services["checkin"].add_checkin_comment(
            checkin_id, self.dashboard.current_user.name, text, "comment"
        )
        self._on_checkin_selected(checkin_id)
