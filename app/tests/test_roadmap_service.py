from app.db.connector import DBConnector
from app.db.schema import init_db
from app.repositories.roadmap_repository import RoadmapRepository
from app.services.roadmap import RoadmapService


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

    repo = RoadmapRepository(DBConnector(str(db_path)))
    service = RoadmapService(repo)
    roadmap_id = service.create_roadmap(team_id)
    service.submit_roadmap(roadmap_id)
    assert service.get_roadmap_status(roadmap_id) == "Submitted"
    service.approve_roadmap(roadmap_id)
    assert service.get_roadmap_status(roadmap_id) == "Approved"
