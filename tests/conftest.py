import pytest


@pytest.fixture
def app(monkeypatch, tmp_path):
    db_file = tmp_path / "test_spendly.db"
    monkeypatch.setattr("database.db.DB_PATH", str(db_file))

    from app import app as flask_app
    from database.db import init_db

    flask_app.config["TESTING"] = True

    with flask_app.app_context():
        init_db()

    yield flask_app
