from __future__ import annotations

import tkinter as tk
from libs.ui_kit import CommentThread, Section
from ui.student.pages.base import StudentSectionPage


class StudentCommentsPage(StudentSectionPage):
    title = "Comments"
    route = "comments"
    subtitle = "Roadmap feedback and discussion history."

    def on_mount(self) -> None:
        super().on_mount()
        
        self.thread_sec = Section(self.body, "Discussion Thread")
        self.thread_sec.pack(fill="both", expand=True)
        
        self.thread = CommentThread(self.thread_sec.body, on_send=self._add_comment)
        self.thread.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self._refresh_comments()

    def _refresh_comments(self) -> None:
        roadmap_id = self.dashboard.current_roadmap_id
        if not roadmap_id:
            self.thread.set_comments([])
            return
            
        comments = self.dashboard.services["roadmap"].list_roadmap_comments(roadmap_id)
        self.thread.set_comments([(c["author"], c["text"], c["created_at"]) for c in comments])

    def _add_comment(self, text: str) -> None:
        roadmap_id = self.dashboard.current_roadmap_id
        if roadmap_id:
            self.dashboard.services["roadmap"].add_roadmap_comment(
                roadmap_id, self.dashboard.current_user.name, text, "comment"
            )
            self._refresh_comments()
