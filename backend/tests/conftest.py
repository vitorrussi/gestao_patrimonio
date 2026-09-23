from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.db import Base


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Flask]:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    # Evita que um DATABASE_URL vindo do .env aponte os testes para o banco real.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    flask_app = create_app()
    engine = flask_app.extensions["db_engine"]
    Base.metadata.create_all(engine)
    yield flask_app
    engine.dispose()


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()
