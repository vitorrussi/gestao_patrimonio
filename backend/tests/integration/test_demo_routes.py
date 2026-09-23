from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Property, User
from scripts.seed_demo import DEMO_EMAIL


def test_reset_returns_404_when_not_demo(logged_client: FlaskClient) -> None:
    response = logged_client.post("/api/demo/reset")

    assert response.status_code == 404


def test_reset_requires_login(app: Flask, client: FlaskClient) -> None:
    app.config["IS_DEMO"] = True

    response = client.post("/api/demo/reset")

    assert response.status_code == 401


def test_reset_creates_and_rebuilds_demo_portfolio(
    app: Flask, logged_client: FlaskClient, db_session: Session
) -> None:
    app.config["IS_DEMO"] = True

    first = logged_client.post("/api/demo/reset")
    assert first.status_code == 204
    demo_user = db_session.scalar(select(User).where(User.email == DEMO_EMAIL))
    assert demo_user is not None
    properties = db_session.scalars(select(Property).where(Property.user_id == demo_user.id)).all()
    assert len(properties) == 6  # mesma carteira fictícia do scripts/seed_demo.py

    # rodar de novo mantém a mesma conta (o id não muda) e não acumula duplicatas.
    second = logged_client.post("/api/demo/reset")
    assert second.status_code == 204
    same_user = db_session.scalar(select(User).where(User.email == DEMO_EMAIL))
    assert same_user is not None
    assert same_user.id == demo_user.id
