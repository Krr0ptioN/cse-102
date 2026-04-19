from __future__ import annotations

from .base import Repository


class TeamRepository(Repository):
    def create_team(self, class_id: int, name: str, principal_user_id: int | None) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO teams(class_id, name, principal_user_id) VALUES (?, ?, ?)",
                (class_id, name, principal_user_id),
            )
            return int(cur.lastrowid)

    def update_team_principal(self, team_id: int, principal_user_id: int | None) -> None:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "SELECT principal_user_id FROM teams WHERE id = ?",
                (team_id,),
            )
            row = cur.fetchone()
            previous_principal = row[0] if row else None
            conn.execute(
                "UPDATE teams SET principal_user_id = ? WHERE id = ?",
                (principal_user_id, team_id),
            )
            if previous_principal and previous_principal != principal_user_id:
                conn.execute(
                    "UPDATE team_members SET role = ? WHERE team_id = ? AND user_id = ?",
                    ("Member", team_id, previous_principal),
                )
            if principal_user_id:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO team_members(team_id, user_id, role)
                    VALUES (?, ?, ?)
                    """,
                    (team_id, principal_user_id, "Principal"),
                )
                conn.execute(
                    "UPDATE team_members SET role = ? WHERE team_id = ? AND user_id = ?",
                    ("Principal", team_id, principal_user_id),
                )

    def add_team_member(self, team_id: int, user_id: int, role: str = "Member") -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO team_members(team_id, user_id, role) VALUES (?, ?, ?)",
                (team_id, user_id, role),
            )
            conn.execute(
                "UPDATE team_invitations SET status = ? WHERE team_id = ? AND user_id = ?",
                ("Accepted", team_id, user_id),
            )

    def list_teams(self, class_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT teams.id, teams.name, teams.principal_user_id, users.name
                FROM teams
                LEFT JOIN users ON users.id = teams.principal_user_id
                WHERE teams.class_id = ?
                ORDER BY teams.name
                """,
                (class_id,),
            )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "principal_user_id": row[2],
                    "principal_name": row[3],
                }
                for row in cur.fetchall()
            ]

    def list_team_members(self, team_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT users.id, users.name, users.email, team_members.role
                FROM team_members
                JOIN users ON users.id = team_members.user_id
                WHERE team_members.team_id = ?
                ORDER BY users.name
                """,
                (team_id,),
            )
            return [
                {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
                for row in cur.fetchall()
            ]

    def set_member_role(self, team_id: int, user_id: int, role: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE team_members SET role = ? WHERE team_id = ? AND user_id = ?",
                (role, team_id, user_id),
            )

    def list_teams_for_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT teams.id, teams.name, teams.class_id, teams.principal_user_id, users.name
                FROM team_members
                JOIN teams ON teams.id = team_members.team_id
                LEFT JOIN users ON users.id = teams.principal_user_id
                WHERE team_members.user_id = ?
                ORDER BY teams.name
                """,
                (user_id,),
            )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "class_id": row[2],
                    "principal_user_id": row[3],
                    "principal_name": row[4],
                }
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
                """
                SELECT teams.id, teams.name, teams.class_id, teams.principal_user_id, users.name
                FROM teams
                LEFT JOIN users ON users.id = teams.principal_user_id
                ORDER BY teams.name
                """
            )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "class_id": row[2],
                    "principal_user_id": row[3],
                    "principal_name": row[4],
                }
                for row in cur.fetchall()
            ]

    def get_team(self, team_id: int) -> dict | None:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT teams.id, teams.name, teams.class_id, teams.principal_user_id, users.name
                FROM teams
                LEFT JOIN users ON users.id = teams.principal_user_id
                WHERE teams.id = ?
                """,
                (team_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "name": row[1],
                "class_id": row[2],
                "principal_user_id": row[3],
                "principal_name": row[4],
            }

    def create_invitation(self, team_id: int, user_id: int, created_at: str) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                """
                INSERT INTO team_invitations(team_id, user_id, status, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (team_id, user_id, "Pending", created_at),
            )
            return int(cur.lastrowid)

    def list_invitations_for_user(self, user_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT team_invitations.id, teams.name, team_invitations.status
                FROM team_invitations
                JOIN teams ON teams.id = team_invitations.team_id
                WHERE team_invitations.user_id = ?
                ORDER BY team_invitations.created_at DESC
                """,
                (user_id,),
            )
            return [
                {"id": row[0], "team": row[1], "status": row[2]}
                for row in cur.fetchall()
            ]

    def set_invitation_status(self, invitation_id: int, status: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE team_invitations SET status = ? WHERE id = ?",
                (status, invitation_id),
            )

    def accept_invitation(self, invitation_id: int) -> bool:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "SELECT team_id, user_id FROM team_invitations WHERE id = ?",
                (invitation_id,),
            )
            row = cur.fetchone()
            if not row:
                return False
            team_id, user_id = int(row[0]), int(row[1])
            conn.execute(
                "UPDATE team_invitations SET status = ? WHERE id = ?",
                ("Accepted", invitation_id),
            )
            conn.execute(
                "INSERT OR IGNORE INTO team_members(team_id, user_id, role) VALUES (?, ?, ?)",
                (team_id, user_id, "Member"),
            )
            return True

    def list_invitations_for_team(self, team_id: int) -> list[dict]:
        with self.db.connect() as conn:
            cur = conn.execute(
                """
                SELECT team_invitations.id, users.name, team_invitations.status
                FROM team_invitations
                JOIN users ON users.id = team_invitations.user_id
                WHERE team_invitations.team_id = ?
                ORDER BY team_invitations.created_at DESC
                """,
                (team_id,),
            )
            return [
                {"id": row[0], "user": row[1], "status": row[2]}
                for row in cur.fetchall()
            ]
