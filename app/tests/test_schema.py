from core.db.schema import init_db
from core.db.connector import DBConnector
from core.repositories import SchemaRepository
from core.services import SchemaService


def test_schema_creates_tables(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    repo = SchemaRepository(DBConnector(str(db_path)))
    tables = set(SchemaService(repo).list_tables())
    assert {
        "users",
        "classes",
        "app_metadata",
        "teams",
        "team_members",
        "roadmaps",
        "phases",
        "tasks",
        "updates",
        "roadmap_comments",
        "checkins",
        "checkin_comments",
        "team_invitations",
    }.issubset(tables)
