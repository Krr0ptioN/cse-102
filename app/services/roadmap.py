from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.services.base import Service


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
    def __init__(self, db: DBConnector) -> None:
        super().__init__(db)

    def create_roadmap(self, team_id: int) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO roadmaps(team_id, status, created_at) VALUES (?, ?, ?)",
                (team_id, STATUS_DRAFT, datetime.utcnow().isoformat()),
            )
            return int(cur.lastrowid)

    def submit_roadmap(self, roadmap_id: int) -> None:
        self._transition_status(roadmap_id, STATUS_SUBMITTED)

    def approve_roadmap(self, roadmap_id: int) -> None:
        self._transition_status(roadmap_id, STATUS_APPROVED)

    def get_roadmap_status(self, roadmap_id: int) -> str | None:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT status FROM roadmaps WHERE id = ?",
                (roadmap_id,),
            )
            row = cur.fetchone()
            return row[0] if row else None

    def list_roadmaps_for_class(self, class_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT roadmaps.id, teams.name, roadmaps.status, users.name
                FROM roadmaps
                JOIN teams ON teams.id = roadmaps.team_id
                LEFT JOIN users ON users.id = teams.principal_user_id
                WHERE teams.class_id = ?
                ORDER BY roadmaps.id
                """,
                (class_id,),
            )
            return [
                {"id": row[0], "team": row[1], "status": row[2], "principal": row[3]}
                for row in cur.fetchall()
            ]

    def add_roadmap_comment(
        self, roadmap_id: int, author: str, text: str, kind: str = "comment"
    ) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO roadmap_comments(roadmap_id, author, text, created_at, kind)
                VALUES (?, ?, ?, ?, ?)
                """,
                (roadmap_id, author, text, datetime.utcnow().isoformat(), kind),
            )

    def list_roadmap_comments(self, roadmap_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT author, text, created_at, kind
                FROM roadmap_comments
                WHERE roadmap_id = ?
                ORDER BY created_at DESC
                """,
                (roadmap_id,),
            )
            return [
                {
                    "author": row[0],
                    "text": row[1],
                    "created_at": row[2],
                    "kind": row[3],
                }
                for row in cur.fetchall()
            ]

    def get_latest_roadmap(self, team_id: int) -> dict | None:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT id, status, created_at
                FROM roadmaps
                WHERE team_id = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (team_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {"id": row[0], "status": row[1], "created_at": row[2]}

    def create_phase(self, roadmap_id: int, name: str, sort_order: int) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO phases(roadmap_id, name, sort_order) VALUES (?, ?, ?)",
                (roadmap_id, name, sort_order),
            )
            return int(cur.lastrowid)

    def create_task(
        self,
        phase_id: int,
        title: str,
        weight: int,
        assignee_user_id: int | None = None,
    ) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                """
                INSERT INTO tasks(phase_id, title, weight, status, assignee_user_id, notes)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (phase_id, title, weight, "Pending", assignee_user_id, None),
            )
            return int(cur.lastrowid)

    def list_phases_with_tasks(self, roadmap_id: int) -> list[dict]:
        with self.db.connect() as conn:
            phase_rows = conn.execute(
                "SELECT id, name FROM phases WHERE roadmap_id = ? ORDER BY sort_order",
                (roadmap_id,),
            ).fetchall()
            phases = []
            for phase_id, name in phase_rows:
                task_rows = conn.execute(
                    "SELECT id, title, weight, status FROM tasks WHERE phase_id = ? ORDER BY id",
                    (phase_id,),
                ).fetchall()
                tasks = [
                    {"id": row[0], "title": row[1], "weight": row[2], "status": row[3]}
                    for row in task_rows
                ]
                phases.append({"id": phase_id, "name": name, "tasks": tasks})
            return phases

    def update_phase(self, phase_id: int, name: str) -> None:
        with self.db.transaction() as conn:
            conn.execute("UPDATE phases SET name = ? WHERE id = ?", (name, phase_id))

    def delete_phase(self, phase_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM phases WHERE id = ?", (phase_id,))

    def update_task_details(self, task_id: int, title: str, weight: int) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE tasks SET title = ?, weight = ? WHERE id = ?",
                (title, weight, task_id),
            )

    def delete_task(self, task_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def _transition_status(self, roadmap_id: int, target: str) -> None:
        current = self.get_roadmap_status(roadmap_id)
        if current is None:
            raise ValueError("Roadmap not found")
        state = STATES.get(current)
        if state is None or not state.can_transition(target):
            raise ValueError(f"Invalid transition from {current} to {target}")
        self._set_status(roadmap_id, target)

    def _set_status(self, roadmap_id: int, status: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE roadmaps SET status = ? WHERE id = ?",
                (status, roadmap_id),
            )
