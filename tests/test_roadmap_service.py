from app.db.connector import DBConnector
from app.db.schema import init_db
from app.services.roadmap_service import (
    approve_roadmap,
    create_roadmap,
    get_roadmap_status,
    submit_roadmap,
)


def test_submit_and_approve(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    db = DBConnector(str(db_path))
    with db.transaction() as conn:
        cur = conn.execute(
            "INSERT INTO classes(name, term) VALUES (?, ?)",
            ("CSE 102", "Spring 2026"),
        )
        class_id = int(cur.lastrowid)
        cur = conn.execute(
            "INSERT INTO teams(class_id, name, principal_user_id) VALUES (?, ?, ?)",
            (class_id, "Team A", None),
        )
        team_id = int(cur.lastrowid)

    roadmap_id = create_roadmap(str(db_path), team_id=team_id)
    submit_roadmap(str(db_path), roadmap_id)
    assert get_roadmap_status(str(db_path), roadmap_id) == "Submitted"
    approve_roadmap(str(db_path), roadmap_id)
    assert get_roadmap_status(str(db_path), roadmap_id) == "Approved"
