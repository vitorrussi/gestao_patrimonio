"""Usuário B não lê, não altera e não usa nada do usuário A (regra 2)."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.auth import PUBLIC_API_ENDPOINTS
from tests.api_helpers import (
    balance_payload,
    create_balance,
    create_expense,
    create_financing,
    create_property,
    create_valuation,
    expense_payload,
    financing_payload,
    pay,
    valuation_payload,
)


@pytest.fixture()
def owner_data(logged_client: FlaskClient) -> dict[str, int]:
    """Um registro de cada entidade, todos do usuário A."""
    prop = create_property(logged_client)
    financing = create_financing(logged_client, prop["id"])
    expense = create_expense(logged_client, prop["id"])
    payment = pay(logged_client, "recurring_expense", expense["id"], "2026-01-05").get_json()
    return {
        "property": prop["id"],
        "valuation": create_valuation(logged_client, prop["id"])["id"],
        "financing": financing["id"],
        "balance": create_balance(logged_client, financing["id"])["id"],
        "expense": expense["id"],
        "payment": payment["id"],
    }


RECORD_URLS = {
    "property": "/api/properties/{}",
    "valuation": "/api/valuations/{}",
    "financing": "/api/financings/{}",
    "balance": "/api/balances/{}",
    "expense": "/api/expenses/{}",
    "payment": "/api/payments/{}",
}


@pytest.mark.parametrize("entity", list(RECORD_URLS))
@pytest.mark.parametrize("method", ["patch", "delete"])
def test_other_user_cannot_change_or_delete(
    other_client: FlaskClient, owner_data: dict[str, int], entity: str, method: str
) -> None:
    url = RECORD_URLS[entity].format(owner_data[entity])

    response = getattr(other_client, method)(url, json={})

    assert response.status_code == 404


def test_other_user_cannot_read_property(
    other_client: FlaskClient, owner_data: dict[str, int]
) -> None:
    assert other_client.get(f"/api/properties/{owner_data['property']}").status_code == 404


@pytest.mark.parametrize(
    ("url", "parent", "body"),
    [
        ("/api/properties/{}/valuations", "property", valuation_payload()),
        ("/api/properties/{}/financings", "property", financing_payload()),
        ("/api/properties/{}/expenses", "property", expense_payload()),
        ("/api/financings/{}/balances", "financing", balance_payload()),
    ],
)
def test_other_user_cannot_create_records_under_owner_data(
    other_client: FlaskClient, owner_data: dict[str, int], url: str, parent: str, body: dict
) -> None:
    response = other_client.post(url.format(owner_data[parent]), json=body)

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("kind", "entity"), [("recurring_expense", "expense"), ("financing", "financing")]
)
def test_other_user_cannot_pay_owner_dues(
    other_client: FlaskClient, owner_data: dict[str, int], kind: str, entity: str
) -> None:
    response = pay(other_client, kind, owner_data[entity], "2026-02-10")

    assert response.status_code == 404


def test_other_user_views_are_empty(other_client: FlaskClient, owner_data: dict[str, int]) -> None:
    assert other_client.get("/api/properties").get_json() == []
    assert other_client.get("/api/dashboard").get_json()["property_count"] == 0
    assert other_client.get("/api/commitments?year=2026&month=1").get_json()["items"] == []
    assert other_client.get("/api/dues?start=2026-01-01&end=2026-12-31").get_json()["items"] == []


def test_owner_data_is_untouched_after_other_user_attempts(
    logged_client: FlaskClient, other_client: FlaskClient, owner_data: dict[str, int]
) -> None:
    for entity, template in RECORD_URLS.items():
        other_client.delete(template.format(owner_data[entity]))

    detail = logged_client.get(f"/api/properties/{owner_data['property']}").get_json()

    assert len(detail["valuations"]) == 1
    assert len(detail["financings"][0]["balances"]) == 1
    assert len(detail["expenses"]) == 1
    assert len(detail["payments"]) == 1


def test_each_user_sees_only_own_properties(
    logged_client: FlaskClient, other_client: FlaskClient, owner_data: dict[str, int]
) -> None:
    create_property(other_client, nickname="Casa da outra pessoa")

    assert [p["nickname"] for p in logged_client.get("/api/properties").get_json()] == [
        "Apto Centro"
    ]
    assert [p["nickname"] for p in other_client.get("/api/properties").get_json()] == [
        "Casa da outra pessoa"
    ]


# --- sem login: toda rota /api fora das públicas responde 401 ---


def _protected_routes(app: Flask) -> list[tuple[str, str]]:
    routes = []
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith("/api") or rule.endpoint in PUBLIC_API_ENDPOINTS:
            continue
        url = rule.rule
        for argument in rule.arguments:
            url = url.replace(f"<int:{argument}>", "1")
        methods = (rule.methods or set()) - {"HEAD", "OPTIONS"}
        routes += [(method, url) for method in sorted(methods)]
    return routes


def test_every_protected_route_requires_login(app: Flask, client: FlaskClient) -> None:
    routes = _protected_routes(app)

    assert len(routes) >= 20  # garante que a varredura encontrou as rotas
    for method, url in routes:
        response = client.open(url, method=method, json={})
        assert response.status_code == 401, (method, url)
