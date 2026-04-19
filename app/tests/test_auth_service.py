from core.db.connector import DBConnector
from core.db.schema import init_db
from core.repositories import AuthRepository
from core.repositories import ClassRepository
from core.services import AuthService


def test_sign_up_and_sign_in(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    auth = AuthService(AuthRepository(DBConnector(str(db_path))))
    created = auth.sign_up(
        "Teacher One", "teacher@example.edu", "password123", "teacher"
    )

    assert created.id > 0
    assert created.role == "teacher"
    assert created.email == "teacher@example.edu"

    signed_in = auth.sign_in("teacher@example.edu", "password123")
    assert signed_in.id == created.id
    assert signed_in.name == "Teacher One"


def test_sign_up_claims_existing_user_without_credentials(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    db = DBConnector(str(db_path))
    class_repo = ClassRepository(db)
    user_id = class_repo.create_user("Ava", "ava@example.edu", "student")

    auth = AuthService(AuthRepository(db))
    created = auth.sign_up("Ava", "ava@example.edu", "password123", "student")

    assert created.id == user_id
    signed_in = auth.sign_in("ava@example.edu", "password123")
    assert signed_in.id == user_id


def test_sign_up_rejects_existing_credentialed_email(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    auth = AuthService(AuthRepository(DBConnector(str(db_path))))
    auth.sign_up("User One", "user@example.edu", "password123", "student")

    try:
        auth.sign_up("Other", "user@example.edu", "password123", "student")
    except ValueError as exc:
        assert "already exists" in str(exc)
    else:
        raise AssertionError("Expected duplicate email to be rejected")


def test_sign_in_rejects_wrong_password(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    auth = AuthService(AuthRepository(DBConnector(str(db_path))))
    auth.sign_up("User", "user@example.edu", "password123", "student")

    try:
        auth.sign_in("user@example.edu", "wrongpass")
    except ValueError as exc:
        assert "Invalid email or password" in str(exc)
    else:
        raise AssertionError("Expected wrong password to be rejected")
