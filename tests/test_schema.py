from app.db.schema import init_db
from app.db.connector import DBConnector
from app.services.schema import SchemaService


def test_schema_creates_tables(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    tables = set(SchemaService(DBConnector(str(db_path))).list_tables())
    assert {
        "users",
        "classes",
        "teams",
        "team_members",
        "roadmaps",
        "phases",
        "tasks",
        "updates",
        "roadmap_comments",
    }.issubset(tables)
