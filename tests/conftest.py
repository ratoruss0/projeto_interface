from pathlib import Path
from uuid import uuid4

import os

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret")

import db
import pytest
from app import app as flask_app


@pytest.fixture()
def app(monkeypatch):
    data_dir = Path.cwd() / ".test-data"
    data_dir.mkdir(exist_ok=True)
    database_path = data_dir / f"{uuid4().hex}.sqlite3"
    monkeypatch.setattr(db, "SQLITE_PATH", str(database_path))
    monkeypatch.setattr(db, "_engine", "sqlite")
    flask_app.config.update(TESTING=True, SECRET_KEY="test-secret")

    yield flask_app

    monkeypatch.setattr(db, "_engine", None)
    if database_path.exists():
        database_path.unlink()


@pytest.fixture()
def client(app):
    return app.test_client()
