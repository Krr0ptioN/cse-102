from app.db.schema import init_db
from app.db.connector import DBConnector
from app.services.class import ClassService


def test_create_class_and_user(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    service = ClassService(DBConnector(str(db_path)))
    class_id = service.create_class("CSE 102", "Spring 2026")
    user_id = service.create_user("Ava", "ava@example.com", "student")
    assert class_id > 0
    assert user_id > 0
