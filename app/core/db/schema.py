from app.core.db.connector import DBConnector

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    role TEXT NOT NULL,
    password_hash TEXT,
    password_salt TEXT,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT,
    last_login_at TEXT
);

CREATE TABLE IF NOT EXISTS classes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    term TEXT NOT NULL,
    owner_user_id INTEGER,
    FOREIGN KEY(owner_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS app_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    class_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    principal_user_id INTEGER,
    FOREIGN KEY(class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY(principal_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS team_members (
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL DEFAULT 'Member',
    PRIMARY KEY(team_id, user_id),
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roadmaps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS phases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sort_order INTEGER NOT NULL,
    FOREIGN KEY(roadmap_id) REFERENCES roadmaps(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phase_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    weight INTEGER NOT NULL,
    status TEXT NOT NULL,
    assignee_user_id INTEGER,
    notes TEXT,
    FOREIGN KEY(phase_id) REFERENCES phases(id) ON DELETE CASCADE,
    FOREIGN KEY(assignee_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS roadmap_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    roadmap_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    FOREIGN KEY(roadmap_id) REFERENCES roadmaps(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    week_start TEXT NOT NULL,
    week_end TEXT NOT NULL,
    status TEXT NOT NULL,
    wins TEXT NOT NULL,
    risks TEXT NOT NULL,
    next_goal TEXT NOT NULL,
    help_needed TEXT,
    metrics_total INTEGER NOT NULL,
    metrics_done INTEGER NOT NULL,
    metrics_percent INTEGER NOT NULL,
    submitted_at TEXT NOT NULL,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS checkin_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    checkin_id INTEGER NOT NULL,
    author TEXT NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    kind TEXT NOT NULL,
    FOREIGN KEY(checkin_id) REFERENCES checkins(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS team_invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(team_id) REFERENCES teams(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""


def init_db(db_path: str) -> None:
    db = DBConnector(db_path)
    with db.transaction() as conn:
        conn.executescript(SCHEMA_SQL)
        _ensure_team_member_role(conn)
        _ensure_user_auth_columns(conn)
        _ensure_classes_owner_user_id(conn)
        _ensure_app_metadata(conn)


def _ensure_team_member_role(conn) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(team_members)")}
    if "role" not in cols:
        conn.execute(
            "ALTER TABLE team_members ADD COLUMN role TEXT NOT NULL DEFAULT 'Member'"
        )


def _ensure_user_auth_columns(conn) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
    if "password_hash" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_hash TEXT")
    if "password_salt" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN password_salt TEXT")
    if "is_active" not in cols:
        conn.execute(
            "ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"
        )
    if "created_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    conn.execute(
        "UPDATE users SET created_at = datetime('now') WHERE created_at IS NULL"
    )
    if "last_login_at" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN last_login_at TEXT")


def _ensure_classes_owner_user_id(conn) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(classes)")}
    if "owner_user_id" not in cols:
        conn.execute(
            "ALTER TABLE classes ADD COLUMN owner_user_id INTEGER REFERENCES users(id)"
        )


def _ensure_app_metadata(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_metadata (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
