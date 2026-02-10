from __future__ import annotations

from app.db.connection import get_connection


def create_class(db_path: str, name: str, term: str) -> int:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO classes(name, term) VALUES (?, ?)",
            (name, term),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def create_user(db_path: str, name: str, email: str, role: str) -> int:
    conn = get_connection(db_path)
    try:
        cur = conn.execute(
            "INSERT INTO users(name, email, role) VALUES (?, ?, ?)",
            (name, email, role),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def list_users(db_path: str, role: str | None = None) -> list[dict]:
    conn = get_connection(db_path)
    try:
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
    finally:
        conn.close()


def update_user(db_path: str, user_id: int, name: str, email: str) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id),
        )
        conn.commit()
    finally:
        conn.close()


def delete_user(db_path: str, user_id: int) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()
