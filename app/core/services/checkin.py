from __future__ import annotations

from datetime import UTC, datetime

from core.repositories import CheckinRepository
from .base import Service


class CheckinService(Service):
    def __init__(self, repo: CheckinRepository) -> None:
        super().__init__(repo)

    def compute_metrics(self, team_id: int) -> dict:
        total, done = self.repo.get_latest_roadmap_metrics_totals(team_id)
        percent = int(round((done / total) * 100)) if total else 0
        return {"total": total, "done": done, "percent": percent}

    def checkin_exists(self, team_id: int, week_start: str) -> bool:
        return self.repo.checkin_exists(team_id, week_start)

    def create_checkin(
        self,
        team_id: int,
        week_start: str,
        week_end: str,
        status: str,
        wins: str,
        risks: str,
        next_goal: str,
        help_needed: str | None,
        metrics: dict,
    ) -> int:
        return self.repo.create_checkin(
            team_id,
            week_start,
            week_end,
            status,
            wins,
            risks,
            next_goal,
            help_needed,
            metrics["total"],
            metrics["done"],
            metrics["percent"],
            datetime.now(UTC).isoformat(),
        )

    def list_checkins_for_class(self, class_id: int) -> list[dict]:
        return self.repo.list_checkins_for_class(class_id)

    def list_checkins_for_team(self, team_id: int) -> list[dict]:
        return self.repo.list_checkins_for_team(team_id)

    def get_checkin(self, checkin_id: int) -> dict | None:
        return self.repo.get_checkin(checkin_id)

    def add_checkin_comment(
        self, checkin_id: int, author: str, text: str, kind: str
    ) -> None:
        self.repo.add_checkin_comment(
            checkin_id,
            author,
            text,
            datetime.now(UTC).isoformat(),
            kind,
        )

    def approve_checkin(self, checkin_id: int) -> None:
        self.repo.approve_checkin(checkin_id)

    def update_checkin_status(self, checkin_id: int, status: str) -> None:
        self.repo.update_checkin_status(checkin_id, status)

    def list_checkin_comments(self, checkin_id: int) -> list[dict]:
        return self.repo.list_checkin_comments(checkin_id)
