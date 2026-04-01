from __future__ import annotations

from app.repositories.base import Repository


class TaskRepository(Repository):
    def update_task_status(self, task_id: int, status: str) -> None:
        with self.db.transaction() as conn:
            conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))

    def list_tasks_for_roadmap(self, roadmap_id: int) -> list[dict]:
        with self.db.connect() as conn:
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

    def add_update(self, task_id: int, user_id: int, text: str, created_at: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT INTO updates(task_id, user_id, text, created_at) VALUES (?, ?, ?, ?)",
                (task_id, user_id, text, created_at),
            )

    def list_updates_for_task(self, task_id: int) -> list[dict]:
        with self.db.connect() as conn:
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

    def list_tasks_for_class(self, class_id: int) -> list[dict]:
        with self.db.connect() as conn:
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

    def list_tasks_for_team(self, team_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT tasks.id, tasks.title, tasks.weight, tasks.status
                FROM tasks
                JOIN phases ON phases.id = tasks.phase_id
                JOIN roadmaps ON roadmaps.id = phases.roadmap_id
                WHERE roadmaps.team_id = ?
                ORDER BY tasks.id
                """,
                (team_id,),
            )
            return [
                {"id": row[0], "title": row[1], "weight": row[2], "status": row[3]}
                for row in cur.fetchall()
            ]
