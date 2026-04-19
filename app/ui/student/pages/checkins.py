from __future__ import annotations

from ui.student.pages.base import StudentSectionPage
from ui.student.checkins import StudentCheckinsSection


class StudentCheckinsPage(StudentSectionPage):
    title = "Check-ins"
    route = "checkins"
    subtitle = "Weekly status reports and progress metrics."

    def on_mount(self) -> None:
        super().on_mount()
        d = self.dashboard
        self.section = StudentCheckinsSection(
            self.body,
            d._submit_checkin,
        )
        self.section.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self.dashboard._refresh_checkins()
