from datetime import date

import pytest
from flask.testing import FlaskClient

from app import clock
from tests.api_helpers import (
    create_balance,
    create_expense,
    create_financing,
    create_property,
    create_valuation,
    pay,
)

TODAY = date(2026, 6, 10)


@pytest.fixture(autouse=True)
def _frozen_today(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(clock, "today", lambda: TODAY)


@pytest.fixture()
def scenario(logged_client: FlaskClient) -> dict:
    """Carteira com os casos que o painel e os compromissos precisam tratar."""
    main = create_property(logged_client, nickname="Apto Centro", ownership_percentage="50")
    create_valuation(logged_client, main["id"], valuation_date="2026-01-01", value_cents=40_000_000)
    financing = create_financing(logged_client, main["id"])  # parcela dia 10, R$ 2.500,00
    create_balance(logged_client, financing["id"], balance_cents=10_000_000)
    paid_off = create_financing(logged_client, main["id"], lender="Construtora", is_paid_off=True)
    condo = create_expense(logged_client, main["id"])  # mensal, dia 5, R$ 650,00
    iptu = create_expense(
        logged_client,
        main["id"],
        expense_type="iptu",
        description="IPTU 2026 — 10x",
        amount_cents=30_000,
        due_day=10,
        start_date="2026-02-01",
        installment_count=10,
    )
    insurance = create_expense(
        logged_client,
        main["id"],
        expense_type="seguro",
        description="Seguro anual",
        amount_cents=120_000,
        frequency="anual",
        due_day=8,
        start_date="2026-06-01",
    )

    land = create_property(
        logged_client, nickname="Terreno", property_type="terreno", usage="vazio"
    )
    create_expense(logged_client, land["id"], description="Roçada", amount_cents=10_000, due_day=20)

    sold = create_property(logged_client, nickname="Casa vendida", property_type="casa")
    create_valuation(logged_client, sold["id"], value_cents=90_000_000)
    create_expense(logged_client, sold["id"], description="Não deve aparecer")
    logged_client.patch(f"/api/properties/{sold['id']}", json={"is_active": False})

    assert (
        pay(logged_client, "recurring_expense", condo["id"], "2026-06-05", 66_300).status_code
        == 201
    )
    return {
        "main": main,
        "financing": financing,
        "paid_off": paid_off,
        "condo": condo,
        "iptu": iptu,
        "insurance": insurance,
        "land": land,
        "sold": sold,
    }


def test_dashboard_of_empty_portfolio(logged_client: FlaskClient) -> None:
    assert logged_client.get("/api/dashboard").get_json() == {
        "gross_total_cents": 0,
        "debt_total_cents": 0,
        "net_total_cents": 0,
        "property_count": 0,
        "count_by_type": {},
        "properties_without_value": 0,
        "debt_estimated": False,
    }


def test_dashboard_totals(logged_client: FlaskClient, scenario: dict) -> None:
    body = logged_client.get("/api/dashboard").get_json()

    assert body == {
        "gross_total_cents": 20_000_000,  # 50% de 400 mil; o vendido não entra
        "debt_total_cents": 10_000_000,  # o quitado não entra
        "net_total_cents": 10_000_000,
        "property_count": 2,
        "count_by_type": {"apartamento": 1, "terreno": 1},
        "properties_without_value": 1,  # o terreno
        "debt_estimated": False,
    }


def test_month_commitments_with_status_and_totals(
    logged_client: FlaskClient, scenario: dict
) -> None:
    body = logged_client.get("/api/commitments?year=2026&month=6").get_json()

    items = [
        (
            i["due_date"],
            i["description"],
            i["status"],
            i["expected_amount_cents"],
            i["amount_paid_cents"],
        )
        for i in body["items"]
    ]
    assert items == [
        ("2026-06-05", "Condomínio", "pago", 65_000, 66_300),  # pago com juros
        ("2026-06-08", "Seguro anual", "atrasado", 120_000, None),
        ("2026-06-10", "Parcela do financiamento — Caixa", "a_pagar", 250_000, None),
        ("2026-06-10", "IPTU 2026 — 10x", "a_pagar", 30_000, None),
        ("2026-06-20", "Roçada", "a_pagar", 10_000, None),
    ]
    # Não aparecem: financiamento quitado, imóvel vendido e o seguro fora de junho.
    assert body["total_expected_cents"] == 475_000
    assert body["total_paid_cents"] == 66_300
    assert body["total_open_cents"] == 410_000
    assert body["total_overdue_cents"] == 120_000
    assert body["today"] == "2026-06-10"


def test_commitment_items_identify_source_and_payment(
    logged_client: FlaskClient, scenario: dict
) -> None:
    items = logged_client.get("/api/commitments?year=2026&month=6").get_json()["items"]
    paid = next(i for i in items if i["status"] == "pago")
    unpaid = next(i for i in items if i["description"] == "Roçada")

    assert paid["source_kind"] == "recurring_expense"
    assert paid["source_id"] == scenario["condo"]["id"]
    assert paid["property_nickname"] == "Apto Centro"
    assert paid["payment_id"] is not None
    assert unpaid["payment_id"] is None
    assert unpaid["property_id"] == scenario["land"]["id"]


def test_commitments_default_to_current_month(logged_client: FlaskClient, scenario: dict) -> None:
    body = logged_client.get("/api/commitments").get_json()

    assert (body["year"], body["month"]) == (2026, 6)


def test_iptu_ends_after_10_installments(logged_client: FlaskClient, scenario: dict) -> None:
    december = logged_client.get("/api/commitments?year=2026&month=12").get_json()

    assert "IPTU 2026 — 10x" not in [i["description"] for i in december["items"]]


@pytest.mark.parametrize(
    "query", ["year=2026", "month=6", "year=2026&month=13", "year=abc&month=1", "foo=1"]
)
def test_invalid_month_query_returns_400(logged_client: FlaskClient, query: str) -> None:
    assert logged_client.get(f"/api/commitments?{query}").status_code == 400


def test_dues_in_period(logged_client: FlaskClient, scenario: dict) -> None:
    body = logged_client.get("/api/dues?start=2026-06-01&end=2026-07-31").get_json()

    assert len(body["items"]) == 9  # 5 em junho + 4 em julho (o seguro é anual)
    assert all("2026-06-01" <= i["due_date"] <= "2026-07-31" for i in body["items"])
    assert body["total_expected_cents"] == sum(i["expected_amount_cents"] for i in body["items"])


@pytest.mark.parametrize(
    "query",
    [
        "start=2026-06-01",
        "start=2026-06-01&end=2026-05-31",
        "start=2026-01-01&end=2027-01-02",
        "start=01/06/2026&end=2026-06-30",
    ],
)
def test_invalid_period_returns_400(logged_client: FlaskClient, query: str) -> None:
    assert logged_client.get(f"/api/dues?{query}").status_code == 400


def test_one_year_period_is_accepted(logged_client: FlaskClient) -> None:
    assert logged_client.get("/api/dues?start=2028-01-01&end=2028-12-31").status_code == 200
