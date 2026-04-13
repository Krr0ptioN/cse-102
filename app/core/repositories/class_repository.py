from __future__ import annotations

from app.core.repositories.base import Repository


class ClassRepository(Repository):
    def create_class(
        self, name: str, term: str, owner_user_id: int | None = None
    ) -> int:
        with self.db.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO classes(name, term, owner_user_id) VALUES (?, ?, ?)",
                (name, term, owner_user_id),
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

    def list_classes(self, owner_user_id: int | None = None) -> list[dict]:
        with self.db.connect() as conn:
            if owner_user_id is None:
                cur = conn.execute(
                    "SELECT id, name, term, owner_user_id FROM classes ORDER BY id"
                )
            else:
                cur = conn.execute(
                    """
                    SELECT id, name, term, owner_user_id
                    FROM classes
                    WHERE owner_user_id = ?
                    ORDER BY id
                    """,
                    (owner_user_id,),
                )
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "term": row[2],
                    "owner_user_id": row[3],
                }
                for row in cur.fetchall()
            ]
