from flask import Flask
from flask.testing import FlaskClient

from app.models import AppMeta


def test_health_with_empty_table_returns_null_database(client: FlaskClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": None}


def test_health_returns_value_read_from_database(app: Flask, client: FlaskClient) -> None:
    session_factory = app.extensions["db_session_factory"]
    with session_factory() as session:
        session.add(AppMeta(chave="status", valor="lido do banco"))
        session.commit()

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "lido do banco"}


def test_unknown_api_route_returns_json_404(client: FlaskClient) -> None:
    response = client.get("/api/inexistente")

    assert response.status_code == 404
    assert response.get_json() == {"error": "not_found"}
