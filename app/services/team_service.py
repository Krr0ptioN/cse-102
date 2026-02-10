from __future__ import annotations

from app.db.connector import DBConnector


def create_team(db_path: str, class_id: int, name: str, principal_user_id: int | None) -> int:
    db = DBConnector(db_path)
    with db.transaction() as conn:
        cur = conn.execute(
            "INSERT INTO teams(class_id, name, principal_user_id) VALUES (?, ?, ?)",
            (class_id, name, principal_user_id),
        )
        return int(cur.lastrowid)


def update_team_principal(db_path: str, team_id: int, principal_user_id: int | None) -> None:
    db = DBConnector(db_path)
    with db.transaction() as conn:
        conn.execute(
            "UPDATE teams SET principal_user_id = ? WHERE id = ?",
            (principal_user_id, team_id),
        )


def add_team_member(db_path: str, team_id: int, user_id: int) -> None:
    db = DBConnector(db_path)
    with db.transaction() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO team_members(team_id, user_id) VALUES (?, ?)",
            (team_id, user_id),
        )


def list_teams(db_path: str, class_id: int) -> list[dict]:
    db = DBConnector(db_path)
    with db.connect() as conn:
        cur = conn.execute(
            "SELECT id, name, principal_user_id FROM teams WHERE class_id = ? ORDER BY name",
            (class_id,),
        )
        return [
            {"id": row[0], "name": row[1], "principal_user_id": row[2]}
            for row in cur.fetchall()
        ]


def list_team_members(db_path: str, team_id: int) -> list[dict]:
    db = DBConnector(db_path)
    with db.connect() as conn:
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


def update_team(db_path: str, team_id: int, name: str) -> None:
    db = DBConnector(db_path)
    with db.transaction() as conn:
        conn.execute("UPDATE teams SET name = ? WHERE id = ?", (name, team_id))


def delete_team(db_path: str, team_id: int) -> None:
    db = DBConnector(db_path)
    with db.transaction() as conn:
        conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))


def list_all_teams(db_path: str) -> list[dict]:
    db = DBConnector(db_path)
    with db.connect() as conn:
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
