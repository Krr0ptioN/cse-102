from __future__ import annotations

from ui.student.pages.base import StudentSectionPage
from ui.student.comments import StudentCommentsSection


class StudentCommentsPage(StudentSectionPage):
    title = "Comments"
    route = "comments"
    subtitle = "Roadmap feedback and discussion history."

    def on_mount(self) -> None:
        super().on_mount()
        d = self.dashboard
        self.section = StudentCommentsSection(
            self.body,
            d._add_comment,
        )
        self.section.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self.dashboard._refresh_comments()
