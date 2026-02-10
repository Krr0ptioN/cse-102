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


def add_roadmap_comment(
    db_path: str, roadmap_id: int, author: str, text: str, kind: str = "comment"
) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            INSERT INTO roadmap_comments(roadmap_id, author, text, created_at, kind)
            VALUES (?, ?, ?, ?, ?)
            """,
            (roadmap_id, author, text, datetime.utcnow().isoformat(), kind),
        )
        conn.commit()
    finally:
        conn.close()


def list_roadmap_comments(db_path: str, roadmap_id: int) -> list[dict]:
    conn = get_connection(db_path)
    try:
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
    finally:
        conn.close()


def get_latest_roadmap(db_path: str, team_id: int) -> dict | None:
    conn = get_connection(db_path)
    try:
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
    finally:
        conn.close()


def create_phase(db_path: str, roadmap_id: int, name: str, sort_order: int) -> int:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO phases(roadmap_id, name, sort_order) VALUES (?, ?, ?)",
            (roadmap_id, name, sort_order),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def create_task(
    db_path: str,
    phase_id: int,
    title: str,
    weight: int,
    assignee_user_id: int | None = None,
) -> int:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """
            INSERT INTO tasks(phase_id, title, weight, status, assignee_user_id, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (phase_id, title, weight, "Pending", assignee_user_id, None),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_phases_with_tasks(db_path: str, roadmap_id: int) -> list[dict]:
    conn = get_connection(db_path)
    try:
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
    finally:
        conn.close()


def update_phase(db_path: str, phase_id: int, name: str) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute("UPDATE phases SET name = ? WHERE id = ?", (name, phase_id))
        conn.commit()
    finally:
        conn.close()


def delete_phase(db_path: str, phase_id: int) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM phases WHERE id = ?", (phase_id,))
        conn.commit()
    finally:
        conn.close()


def update_task_details(db_path: str, task_id: int, title: str, weight: int) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE tasks SET title = ?, weight = ? WHERE id = ?",
            (title, weight, task_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_task(db_path: str, task_id: int) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    finally:
        conn.close()
