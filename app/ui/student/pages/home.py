from __future__ import annotations

from libs.ui_kit import SectionHeader
from ui.shared.page import Page
from ui.student.stats import StudentStatsRow


class StudentHomePage(Page):
    title = "Overview"
    route = "overview"

    def on_mount(self) -> None:
        self.stats_row = StudentStatsRow(self)
        self.stats_row.pack(fill="x", padx=12, pady=(0, 8))

    def on_show(self) -> None:
        # StudentDashboard handles stats refresh for now, 
        # but we could move it here if we refactor more.
        pass
