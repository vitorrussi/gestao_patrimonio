import pytest
from flask import Flask, jsonify
from flask.testing import FlaskClient

from app import create_app
from app.models import User
from tests.constants import USER_EMAIL, USER_PASSWORD

NEW_USER = {"email": "novo@example.com", "password": "senha-nova-123"}


# --- cadastro ---


def test_register_creates_user_and_logs_in(client: FlaskClient) -> None:
    response = client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 201
    body = response.get_json()
    assert body["email"] == "novo@example.com"
    assert set(body) == {"id", "email"}
    assert client.get("/api/auth/me").status_code == 200


def test_register_duplicate_email_returns_409(client: FlaskClient, user: User) -> None:
    response = client.post(
        "/api/auth/register", json={"email": USER_EMAIL.upper(), "password": "outra-senha-123"}
    )

    assert response.status_code == 409
    assert response.get_json() == {"error": "email_already_registered"}


def test_register_disabled_returns_403(app: Flask, client: FlaskClient) -> None:
    app.config["ALLOW_REGISTRATION"] = False

    response = client.post("/api/auth/register", json=NEW_USER)

    assert response.status_code == 403
    assert response.get_json() == {"error": "registration_disabled"}


@pytest.mark.parametrize(
    ("payload", "field"),
    [
        ({"email": "sem-arroba", "password": "senha-nova-123"}, "email"),
        ({"email": "novo@example.com", "password": "curta"}, "password"),
        ({"email": "novo@example.com"}, "password"),
    ],
)
def test_register_invalid_payload_returns_400(
    client: FlaskClient, payload: dict[str, str], field: str
) -> None:
    response = client.post("/api/auth/register", json=payload)

    assert response.status_code == 400
    body = response.get_json()
    assert body["error"] == "validation_error"
    assert [detail["field"] for detail in body["details"]] == [field]


def test_register_does_not_echo_password_in_errors(client: FlaskClient) -> None:
    response = client.post(
        "/api/auth/register", json={"email": "novo@example.com", "password": "curta"}
    )

    assert "curta" not in response.get_data(as_text=True)


def test_register_non_json_body_returns_400(client: FlaskClient) -> None:
    response = client.post("/api/auth/register", data="email=a@b.com&password=12345678")

    assert response.status_code == 400
    assert response.get_json()["details"][0]["type"] == "json_required"


# --- login e logout ---


def test_login_with_correct_credentials(client: FlaskClient, user: User) -> None:
    response = client.post("/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASSWORD})

    assert response.status_code == 200
    assert response.get_json() == {"id": user.id, "email": USER_EMAIL}
    assert client.get("/api/auth/me").get_json() == {"id": user.id, "email": USER_EMAIL}


@pytest.mark.parametrize(
    "credentials",
    [
        {"email": USER_EMAIL, "password": "senha-errada-123"},
        {"email": "ninguem@example.com", "password": USER_PASSWORD},
    ],
)
def test_login_failure_returns_same_401(
    client: FlaskClient, user: User, credentials: dict[str, str]
) -> None:
    response = client.post("/api/auth/login", json=credentials)

    assert response.status_code == 401
    assert response.get_json() == {
        "error": "invalid_credentials",
        "message": "E-mail ou senha inválidos",
    }
    assert client.get("/api/auth/me").status_code == 401


def test_login_invalid_payload_returns_400(client: FlaskClient) -> None:
    response = client.post("/api/auth/login", json={"email": USER_EMAIL})

    assert response.status_code == 400


def test_logout_ends_session(logged_client: FlaskClient) -> None:
    response = logged_client.post("/api/auth/logout")

    assert response.status_code == 204
    assert logged_client.get("/api/auth/me").status_code == 401


# --- proteção das rotas ---


def test_me_without_login_returns_401(client: FlaskClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401
    assert response.get_json() == {"error": "unauthorized"}


def test_logout_without_login_returns_401(client: FlaskClient) -> None:
    assert client.post("/api/auth/logout").status_code == 401


def test_health_stays_public(client: FlaskClient) -> None:
    assert client.get("/api/health").status_code == 200


def test_new_api_route_is_protected_by_default(app: Flask, client: FlaskClient) -> None:
    @app.get("/api/rota-nova-sem-decorator")
    def _new_route():
        return jsonify(ok=True)

    assert client.get("/api/rota-nova-sem-decorator").status_code == 401

    client.post("/api/auth/register", json=NEW_USER)
    assert client.get("/api/rota-nova-sem-decorator").status_code == 200


def test_session_cookie_is_httponly_and_samesite_lax(client: FlaskClient, user: User) -> None:
    response = client.post("/api/auth/login", json={"email": USER_EMAIL, "password": USER_PASSWORD})

    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie


def test_create_app_without_secret_key_fails(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()
