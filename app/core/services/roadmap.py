from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from .base import Service
from core.repositories import RoadmapRepository


STATUS_DRAFT = "Draft"
STATUS_SUBMITTED = "Submitted"
STATUS_APPROVED = "Approved"


@dataclass(frozen=True)
class RoadmapState:
    name: str
    allowed_transitions: set[str]

    def can_transition(self, target: str) -> bool:
        return target in self.allowed_transitions


STATES: dict[str, RoadmapState] = {
    STATUS_DRAFT: RoadmapState(STATUS_DRAFT, {STATUS_SUBMITTED}),
    STATUS_SUBMITTED: RoadmapState(STATUS_SUBMITTED, {STATUS_APPROVED}),
    STATUS_APPROVED: RoadmapState(STATUS_APPROVED, set()),
}


class RoadmapService(Service):
    def __init__(self, repo: RoadmapRepository) -> None:
        super().__init__(repo)

    def create_roadmap(self, team_id: int) -> int:
        return self.repo.create_roadmap(team_id, STATUS_DRAFT, datetime.now(UTC).isoformat())

    def submit_roadmap(self, roadmap_id: int) -> None:
        self._transition_status(roadmap_id, STATUS_SUBMITTED)

    def approve_roadmap(self, roadmap_id: int) -> None:
        self._transition_status(roadmap_id, STATUS_APPROVED)

    def get_roadmap_status(self, roadmap_id: int) -> str | None:
        return self.repo.get_roadmap_status(roadmap_id)

    def list_roadmaps_for_class(self, class_id: int) -> list[dict]:
        return self.repo.list_roadmaps_for_class(class_id)

    def add_roadmap_comment(
        self, roadmap_id: int, author: str, text: str, kind: str = "comment"
    ) -> None:
        self.repo.add_roadmap_comment(
            roadmap_id,
            author,
            text,
            datetime.now(UTC).isoformat(),
            kind,
        )

    def list_roadmap_comments(self, roadmap_id: int) -> list[dict]:
        return self.repo.list_roadmap_comments(roadmap_id)

    def get_latest_roadmap(self, team_id: int) -> dict | None:
        return self.repo.get_latest_roadmap(team_id)

    def create_phase(self, roadmap_id: int, name: str, sort_order: int) -> int:
        return self.repo.create_phase(roadmap_id, name, sort_order)

    def create_task(
        self,
        phase_id: int,
        title: str,
        weight: int,
        assignee_user_id: int | None = None,
    ) -> int:
        return self.repo.create_task(
            phase_id,
            title,
            weight,
            "Pending",
            assignee_user_id,
            None,
        )

    def list_phases_with_tasks(self, roadmap_id: int) -> list[dict]:
        return self.repo.list_phases_with_tasks(roadmap_id)

    def update_phase(self, phase_id: int, name: str) -> None:
        self.repo.update_phase(phase_id, name)

    def delete_phase(self, phase_id: int) -> None:
        self.repo.delete_phase(phase_id)

    def update_task_details(self, task_id: int, title: str, weight: int) -> None:
        self.repo.update_task_details(task_id, title, weight)

    def delete_task(self, task_id: int) -> None:
        self.repo.delete_task(task_id)

    def _transition_status(self, roadmap_id: int, target: str) -> None:
        current = self.get_roadmap_status(roadmap_id)
        if current is None:
            raise ValueError("Roadmap not found")
        state = STATES.get(current)
        if state is None or not state.can_transition(target):
            raise ValueError(f"Invalid transition from {current} to {target}")
        self._set_status(roadmap_id, target)

    def _set_status(self, roadmap_id: int, status: str) -> None:
        self.repo.set_roadmap_status(roadmap_id, status)
