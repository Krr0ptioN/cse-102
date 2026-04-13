from app.core.db.schema import init_db
from app.core.db.connector import DBConnector
from app.core.repositories.schema_repository import SchemaRepository
from app.core.services.schema import SchemaService


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
