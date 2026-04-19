from __future__ import annotations

from ui.student.pages.base import StudentSectionPage
from ui.student.tasks import TaskSection


class StudentTasksPage(StudentSectionPage):
    title = "Tasks"
    route = "tasks"
    subtitle = "Track implementation progress and updates."

    def on_mount(self) -> None:
        super().on_mount()
        d = self.dashboard
        self.section = TaskSection(
            self.body,
            d._refresh_updates,
            d._set_task_status,
            d._add_update,
        )
        self.section.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self.dashboard._refresh_task_list()
