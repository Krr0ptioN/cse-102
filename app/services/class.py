from __future__ import annotations

from app.services.base import Service


class ClassService(Service):
    def __init__(self, db: DBConnector) -> None:
        super().__init__(db)

    def create_class(self, name: str, term: str) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO classes(name, term) VALUES (?, ?)",
                (name, term),
            )
            return int(cur.lastrowid)

    def create_user(self, name: str, email: str, role: str) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO users(name, email, role) VALUES (?, ?, ?)",
                (name, email, role),
            )
            return int(cur.lastrowid)

    def list_users(self, role: str | None = None) -> list[dict]:
        with self.db.connect() as conn:
            if role:
                cur = conn.execute(
                    "SELECT id, name, email, role FROM users WHERE role = ? ORDER BY name",
                    (role,),
                )
            else:
                cur = conn.execute(
                    "SELECT id, name, email, role FROM users ORDER BY name"
                )
            rows = cur.fetchall()
            return [
                {"id": row[0], "name": row[1], "email": row[2], "role": row[3]}
                for row in rows
            ]

    def update_user(self, user_id: int, name: str, email: str) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id),
            )

    def delete_user(self, user_id: int) -> None:
        with self.db.transaction() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
