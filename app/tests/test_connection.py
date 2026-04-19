from core.db.connector import DBConnector


def test_connection_executes_query(tmp_path):
    db_path = tmp_path / "app.db"
    db = DBConnector(str(db_path))
    with db.transaction() as conn:
        conn.execute("CREATE TABLE t(id INTEGER)")
        conn.execute("INSERT INTO t(id) VALUES (1)")
    with db.connect() as conn:
        row = conn.execute("SELECT id FROM t").fetchone()
        assert row[0] == 1
