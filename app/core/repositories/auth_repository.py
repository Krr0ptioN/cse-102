from __future__ import annotations

from app.core.repositories.base import Repository


class AuthRepository(Repository):
    @staticmethod
    def _to_user_dict(row: tuple) -> dict:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "role": row[3],
            "password_hash": row[4],
            "password_salt": row[5],
            "is_active": row[6],
            "created_at": row[7],
            "last_login_at": row[8],
        }

    def find_user_by_email(self, email: str) -> dict | None:
        self.log.debug("Lookup user by email=%s", email)
        with self.db.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, email, role, password_hash, password_salt,
                       is_active, created_at, last_login_at
                FROM users
                WHERE lower(email) = lower(?)
                LIMIT 1
                """,
                (email,),
            ).fetchone()
        if row is None:
            return None
        return self._to_user_dict(row)

    def find_user_by_id(self, user_id: int) -> dict | None:
        self.log.debug("Lookup user by id=%s", user_id)
        with self.db.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, email, role, password_hash, password_salt,
                       is_active, created_at, last_login_at
                FROM users
                WHERE id = ?
                LIMIT 1
                """,
                (user_id,),
            ).fetchone()
        if row is None:
            return None
        return self._to_user_dict(row)

    def create_account(
        self,
        *,
        name: str,
        email: str,
        role: str,
        password_hash: str,
        password_salt: str,
        created_at: str,
    ) -> int:
        self.log.debug("Create account email=%s role=%s", email, role)
        with self.db.transaction() as conn:
            cur = conn.execute(
                """
                INSERT INTO users(
                    name,
                    email,
                    role,
                    password_hash,
                    password_salt,
                    is_active,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (name, email, role, password_hash, password_salt, created_at),
            )
            user_id = int(cur.lastrowid)
            self.log.debug("Created account id=%s email=%s", user_id, email)
            return user_id

    def claim_existing_account(
        self,
        *,
        user_id: int,
        name: str,
        role: str,
        password_hash: str,
        password_salt: str,
        created_at: str,
    ) -> None:
        self.log.debug("Claim existing account user_id=%s role=%s", user_id, role)
        with self.db.transaction() as conn:
            conn.execute(
                """
                UPDATE users
                SET name = ?,
                    role = ?,
                    password_hash = ?,
                    password_salt = ?,
                    is_active = 1,
                    created_at = COALESCE(created_at, ?)
                WHERE id = ?
                """,
                (name, role, password_hash, password_salt, created_at, user_id),
            )

    def set_last_login(self, user_id: int, timestamp: str) -> None:
        self.log.debug("Update last login user_id=%s", user_id)
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE users SET last_login_at = ? WHERE id = ?",
                (timestamp, user_id),
            )

    def update_password(
        self,
        user_id: int,
        password_hash: str,
        password_salt: str,
    ) -> None:
        with self.db.transaction() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, password_salt = ? WHERE id = ?",
                (password_hash, password_salt, user_id),
            )
