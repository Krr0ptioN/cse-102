from __future__ import annotations

from app.services.base import Service


class TeamService(Service):
    def __init__(self, db_path: str) -> None:
        super().__init__(db_path)

    def create_team(self, class_id: int, name: str, principal_user_id: int | None) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO teams(class_id, name, principal_user_id) VALUES (?, ?, ?)",
                (class_id, name, principal_user_id),
            )
            return int(cur.lastrowid)

    def update_team_principal(self, team_id: int, principal_user_id: int | None) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE teams SET principal_user_id = ? WHERE id = ?",
                (principal_user_id, team_id),
            )

    def add_team_member(self, team_id: int, user_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO team_members(team_id, user_id) VALUES (?, ?)",
                (team_id, user_id),
            )

    def list_teams(self, class_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT id, name, principal_user_id FROM teams WHERE class_id = ? ORDER BY name",
                (class_id,),
            )
            return [
                {"id": row[0], "name": row[1], "principal_user_id": row[2]}
                for row in cur.fetchall()
            ]

    def list_team_members(self, team_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT users.id, users.name, users.email
                FROM team_members
                JOIN users ON users.id = team_members.user_id
                WHERE team_members.team_id = ?
                ORDER BY users.name
                """,
                (team_id,),
            )
            return [
                {"id": row[0], "name": row[1], "email": row[2]}
                for row in cur.fetchall()
            ]

    def update_team(self, team_id: int, name: str) -> None:
        with self.db.transaction() as conn:
            conn.execute("UPDATE teams SET name = ? WHERE id = ?", (name, team_id))

    def delete_team(self, team_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))

    def list_all_teams(self) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                "SELECT id, name, class_id, principal_user_id FROM teams ORDER BY name"
            )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "class_id": row[2],
                    "principal_user_id": row[3],
                }
                for row in cur.fetchall()
            ]
