from collections.abc import Iterator
from pathlib import Path

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy.orm import Session

from app import create_app
from app.db import Base
from app.models import User
from app.services.auth import register_user
from tests.constants import USER_EMAIL, USER_PASSWORD


@pytest.fixture()
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Flask]:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    # Evita que um DATABASE_URL vindo do .env aponte os testes para o banco real.
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("SECRET_KEY", "chave-so-para-testes")
    monkeypatch.setenv("ALLOW_REGISTRATION", "true")
    flask_app = create_app()
    engine = flask_app.extensions["db_engine"]
    Base.metadata.create_all(engine)
    yield flask_app
    engine.dispose()


@pytest.fixture()
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture()
def db_session(app: Flask) -> Iterator[Session]:
    with app.extensions["db_session_factory"]() as session:
        yield session


@pytest.fixture()
def user(db_session: Session) -> User:
    return register_user(db_session, USER_EMAIL, USER_PASSWORD)


@pytest.fixture()
def logged_client(client: FlaskClient, user: User) -> FlaskClient:
    response = client.post("/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    assert response.status_code == 200
    return client
