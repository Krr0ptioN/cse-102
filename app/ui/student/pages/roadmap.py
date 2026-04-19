from __future__ import annotations

from ui.student.pages.base import StudentSectionPage
from ui.student.roadmap import RoadmapBuilderSection


class StudentRoadmapPage(StudentSectionPage):
    title = "Roadmap"
    route = "roadmap"
    subtitle = "Manage invites, phases, and task planning."

    def on_mount(self) -> None:
        super().on_mount()
        d = self.dashboard
        self.section = RoadmapBuilderSection(
            self.body,
            d._set_active_student,
            d._accept_invite,
            d._decline_invite,
            d._create_team,
            d._invite_student,
            d._load_roadmap,
            d._add_phase,
            d._edit_phase,
            d._delete_phase,
            d._add_task,
            d._edit_task,
            d._delete_task,
            d._submit_roadmap,
            d._show_charts,
            show_student_selector=False,
        )
        self.section.pack(fill="both", expand=True)

    def on_show(self) -> None:
        self.dashboard._refresh_invitations()
        self.dashboard._refresh_teams()
