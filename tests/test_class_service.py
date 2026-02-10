from app.db.schema import init_db
from app.services.class_service import create_class, create_user


def test_create_class_and_user(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))
    class_id = create_class(str(db_path), "CSE 102", "Spring 2026")
    user_id = create_user(str(db_path), "Ava", "ava@example.com", "student")
    assert class_id > 0
    assert user_id > 0
