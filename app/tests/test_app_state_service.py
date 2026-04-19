from core.db.connector import DBConnector
from core.db.schema import init_db
from core.repositories import AppStateRepository
from core.services import AppStateService


def test_dataset_mode_defaults_to_real(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    service = AppStateService(AppStateRepository(DBConnector(str(db_path))))
    assert service.get_dataset_mode() == "real"


def test_dataset_mode_round_trip(tmp_path):
    db_path = tmp_path / "app.db"
    init_db(str(db_path))

    service = AppStateService(AppStateRepository(DBConnector(str(db_path))))
    service.set_dataset_mode("mock")

    assert service.get_dataset_mode() == "mock"
