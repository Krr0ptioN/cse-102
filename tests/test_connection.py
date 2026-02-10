from app.db.connection import get_connection


def test_connection_executes_query(tmp_path):
    db_path = tmp_path / "app.db"
    conn = get_connection(str(db_path))
    conn.execute("CREATE TABLE t(id INTEGER)")
    conn.execute("INSERT INTO t(id) VALUES (1)")
    conn.commit()
    row = conn.execute("SELECT id FROM t").fetchone()
    assert row[0] == 1
    conn.close()
