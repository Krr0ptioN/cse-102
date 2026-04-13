from __future__ import annotations

from datetime import UTC, datetime

from app.core.repositories.task_repository import TaskRepository
from app.core.services.base import Service


class TaskService(Service):
    def __init__(self, repo: TaskRepository) -> None:
        super().__init__(repo)

    def update_task_status(self, task_id: int, status: str) -> None:
        self.repo.update_task_status(task_id, status)

    def list_tasks_for_roadmap(self, roadmap_id: int) -> list[dict]:
        return self.repo.list_tasks_for_roadmap(roadmap_id)

    def add_update(self, task_id: int, user_id: int, text: str) -> None:
        self.repo.add_update(task_id, user_id, text, datetime.now(UTC).isoformat())

    def list_updates_for_task(self, task_id: int) -> list[dict]:
        return self.repo.list_updates_for_task(task_id)

    def list_tasks_for_class(self, class_id: int) -> list[dict]:
        return self.repo.list_tasks_for_class(class_id)

    def list_tasks_for_team(self, team_id: int) -> list[dict]:
        return self.repo.list_tasks_for_team(team_id)
