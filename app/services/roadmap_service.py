from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.db.connection import get_connection


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


def create_roadmap(db_path: str, team_id: int) -> int:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO roadmaps(team_id, status, created_at) VALUES (?, ?, ?)",
            (team_id, STATUS_DRAFT, datetime.utcnow().isoformat()),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def submit_roadmap(db_path: str, roadmap_id: int) -> None:
    _transition_status(db_path, roadmap_id, STATUS_SUBMITTED)


def approve_roadmap(db_path: str, roadmap_id: int) -> None:
    _transition_status(db_path, roadmap_id, STATUS_APPROVED)


def get_roadmap_status(db_path: str, roadmap_id: int) -> str | None:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "SELECT status FROM roadmaps WHERE id = ?",
            (roadmap_id,),
        )
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()


def _transition_status(db_path: str, roadmap_id: int, target: str) -> None:
    current = get_roadmap_status(db_path, roadmap_id)
    if current is None:
        raise ValueError("Roadmap not found")
    state = STATES.get(current)
    if state is None or not state.can_transition(target):
        raise ValueError(f"Invalid transition from {current} to {target}")
    _set_status(db_path, roadmap_id, target)


def _set_status(db_path: str, roadmap_id: int, status: str) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE roadmaps SET status = ? WHERE id = ?",
            (status, roadmap_id),
        )
        conn.commit()
    finally:
        conn.close()


def list_roadmaps_for_class(db_path: str, class_id: int) -> list[dict]:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """
            SELECT roadmaps.id, teams.name, roadmaps.status
            FROM roadmaps
            JOIN teams ON teams.id = roadmaps.team_id
            WHERE teams.class_id = ?
            ORDER BY roadmaps.id
            """,
            (class_id,),
        )
        return [
            {"id": row[0], "team": row[1], "status": row[2]} for row in cur.fetchall()
        ]
    finally:
        conn.close()
