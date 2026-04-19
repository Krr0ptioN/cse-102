from __future__ import annotations

from .base import Repository


class CheckinRepository(Repository):
    def get_latest_roadmap_metrics_totals(self, team_id: int) -> tuple[int, int]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT
                    COALESCE(SUM(tasks.weight), 0),
                    COALESCE(SUM(CASE WHEN tasks.status = 'Done' THEN tasks.weight ELSE 0 END), 0)
                FROM tasks
                JOIN phases ON phases.id = tasks.phase_id
                JOIN roadmaps ON roadmaps.id = phases.roadmap_id
                WHERE roadmaps.team_id = ?
                  AND roadmaps.id = (
                      SELECT id FROM roadmaps WHERE team_id = ? ORDER BY id DESC LIMIT 1
                  )
                """,
                (team_id, team_id),
            )
            total, done = cur.fetchone()
            return int(total), int(done)

    def checkin_exists(self, team_id: int, week_start: str) -> bool:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT 1 FROM checkins WHERE team_id = ? AND week_start = ? LIMIT 1",
                (team_id, week_start),
            )
            return cur.fetchone() is not None

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
        metrics_total: int,
        metrics_done: int,
        metrics_percent: int,
        submitted_at: str,
    ) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                """
                INSERT INTO checkins(
                    team_id, week_start, week_end, status,
                    wins, risks, next_goal, help_needed,
                    metrics_total, metrics_done, metrics_percent,
                    submitted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    team_id,
                    week_start,
                    week_end,
                    status,
                    wins,
                    risks,
                    next_goal,
                    help_needed,
                    metrics_total,
                    metrics_done,
                    metrics_percent,
                    submitted_at,
                ),
            )
            return int(cur.lastrowid)

    def list_checkins_for_class(self, class_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT checkins.id, teams.name, checkins.week_start, checkins.week_end,
                       checkins.status, checkins.metrics_percent, checkins.submitted_at
                FROM checkins
                JOIN teams ON teams.id = checkins.team_id
                WHERE teams.class_id = ?
                ORDER BY checkins.submitted_at DESC
                """,
                (class_id,),
            )
            return [
                {
                    "id": row[0],
                    "team": row[1],
                    "week_start": row[2],
                    "week_end": row[3],
                    "status": row[4],
                    "percent": row[5],
                    "submitted_at": row[6],
                }
                for row in cur.fetchall()
            ]

    def list_checkins_for_team(self, team_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT id, week_start, week_end, status, metrics_percent, submitted_at
                FROM checkins
                WHERE team_id = ?
                ORDER BY submitted_at DESC
                """,
                (team_id,),
            )
            return [
                {
                    "id": row[0],
                    "week_start": row[1],
                    "week_end": row[2],
                    "status": row[3],
                    "percent": row[4],
                    "submitted_at": row[5],
                }
                for row in cur.fetchall()
            ]

    def get_checkin(self, checkin_id: int) -> dict | None:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT id, team_id, week_start, week_end, status, wins, risks,
                       next_goal, help_needed, metrics_total, metrics_done,
                       metrics_percent, submitted_at
                FROM checkins
                WHERE id = ?
                """,
                (checkin_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "team_id": row[1],
                "week_start": row[2],
                "week_end": row[3],
                "status": row[4],
                "wins": row[5],
                "risks": row[6],
                "next_goal": row[7],
                "help_needed": row[8],
                "metrics_total": row[9],
                "metrics_done": row[10],
                "metrics_percent": row[11],
                "submitted_at": row[12],
            }

    def add_checkin_comment(
        self, checkin_id: int, author: str, text: str, created_at: str, kind: str
    ) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                """
                INSERT INTO checkin_comments(checkin_id, author, text, created_at, kind)
                VALUES (?, ?, ?, ?, ?)
                """,
                (checkin_id, author, text, created_at, kind),
            )

    def approve_checkin(self, checkin_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE checkins SET status = ? WHERE id = ?",
                ("Approved", checkin_id),
            )

    def list_checkin_comments(self, checkin_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT author, text, created_at, kind
                FROM checkin_comments
                WHERE checkin_id = ?
                ORDER BY created_at DESC
                """,
                (checkin_id,),
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
