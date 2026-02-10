from app.db.schema import init_db, list_tables


def test_schema_creates_tables(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    tables = set(list_tables(str(db_path)))
    assert {"users", "classes", "teams", "team_members", "roadmaps", "phases", "tasks", "updates"}.issubset(tables)
