from __future__ import annotations

from datetime import datetime

from app.db.connection import get_connection


def update_task_status(db_path: str, task_id: int, status: str) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
        conn.commit()
    finally:
        conn.close()


def list_tasks_for_roadmap(db_path: str, roadmap_id: int) -> list[dict]:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """
            SELECT tasks.id, tasks.title, tasks.weight, tasks.status
            FROM tasks
            JOIN phases ON phases.id = tasks.phase_id
            WHERE phases.roadmap_id = ?
            ORDER BY tasks.id
            """,
            (roadmap_id,),
        )
        return [
            {"id": row[0], "title": row[1], "weight": row[2], "status": row[3]}
            for row in cur.fetchall()
        ]
    finally:
        conn.close()


def add_update(db_path: str, task_id: int, user_id: int, text: str) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT INTO updates(task_id, user_id, text, created_at) VALUES (?, ?, ?, ?)",
            (task_id, user_id, text, datetime.utcnow().isoformat()),
        )
        conn.commit()
    finally:
        conn.close()


def list_updates_for_task(db_path: str, task_id: int) -> list[dict]:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """
            SELECT updates.id, users.name, updates.text, updates.created_at
            FROM updates
            JOIN users ON users.id = updates.user_id
            WHERE updates.task_id = ?
            ORDER BY updates.created_at DESC
            """,
            (task_id,),
        )
        return [
            {
                "id": row[0],
                "user": row[1],
                "text": row[2],
                "created_at": row[3],
            }
            for row in cur.fetchall()
        ]
    finally:
        conn.close()


def list_tasks_for_class(db_path: str, class_id: int) -> list[dict]:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            """
            SELECT tasks.id, tasks.title, tasks.weight, tasks.status
            FROM tasks
            JOIN phases ON phases.id = tasks.phase_id
            JOIN roadmaps ON roadmaps.id = phases.roadmap_id
            JOIN teams ON teams.id = roadmaps.team_id
            WHERE teams.class_id = ?
            ORDER BY tasks.id
            """,
            (class_id,),
        )
        return [
            {"id": row[0], "title": row[1], "weight": row[2], "status": row[3]}
            for row in cur.fetchall()
        ]
    finally:
        conn.close()
