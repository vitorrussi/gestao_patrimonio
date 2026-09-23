import pytest
from flask.testing import FlaskClient

from tests.api_helpers import (
    create_balance,
    create_expense,
    create_financing,
    create_property,
    create_valuation,
    expense_payload,
    financing_payload,
    pay,
)


@pytest.fixture()
def prop(logged_client: FlaskClient) -> dict:
    return create_property(logged_client)


# --- avaliações ---


def test_valuation_crud(logged_client: FlaskClient, prop: dict) -> None:
    valuation = create_valuation(logged_client, prop["id"])
    assert valuation["value_cents"] == 40_000_000
    assert valuation["property_id"] == prop["id"]

    updated = logged_client.patch(f"/api/valuations/{valuation['id']}", json={"value_cents": 1})
    assert updated.status_code == 200
    assert updated.get_json()["value_cents"] == 1
    assert updated.get_json()["source"] == "corretor"

    assert logged_client.delete(f"/api/valuations/{valuation['id']}").status_code == 204
    assert logged_client.get(f"/api/properties/{prop['id']}").get_json()["valuations"] == []


def test_valuation_with_invalid_source_returns_400(logged_client: FlaskClient, prop: dict) -> None:
    response = logged_client.post(
        f"/api/properties/{prop['id']}/valuations",
        json={"valuation_date": "2026-01-01", "value_cents": 1, "source": "palpite"},
    )

    assert response.status_code == 400


# --- financiamentos e saldos ---


def test_financing_crud(logged_client: FlaskClient, prop: dict) -> None:
    financing = create_financing(logged_client, prop["id"])
    assert financing["annual_interest_rate"] == "9.5000"
    assert financing["current_debt_cents"] == 28_000_000
    assert financing["debt_estimated"] is True

    updated = logged_client.patch(
        f"/api/financings/{financing['id']}", json={"current_installment_cents": 240_000}
    )
    assert updated.status_code == 200
    assert updated.get_json()["current_installment_cents"] == 240_000

    assert logged_client.delete(f"/api/financings/{financing['id']}").status_code == 204


def test_balance_crud_updates_current_debt(logged_client: FlaskClient, prop: dict) -> None:
    financing = create_financing(logged_client, prop["id"])
    balance = create_balance(logged_client, financing["id"])

    detail = logged_client.get(f"/api/properties/{prop['id']}").get_json()
    assert detail["financings"][0]["current_debt_cents"] == 10_000_000
    assert detail["financings"][0]["debt_estimated"] is False

    response = logged_client.patch(f"/api/balances/{balance['id']}", json={"balance_cents": 9_000})
    assert response.get_json()["balance_cents"] == 9_000

    assert logged_client.delete(f"/api/balances/{balance['id']}").status_code == 204
    detail = logged_client.get(f"/api/properties/{prop['id']}").get_json()
    assert detail["financings"][0]["debt_estimated"] is True


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"due_day": 0}, "due_day"),
        ({"due_day": 32}, "due_day"),
        ({"term_months": 0}, "term_months"),
        ({"annual_interest_rate": 9.5}, "annual_interest_rate"),
        ({"amortization_system": "alemao"}, "amortization_system"),
        ({"lender": ""}, "lender"),
    ],
)
def test_invalid_financing_returns_400(
    logged_client: FlaskClient, prop: dict, overrides: dict, field: str
) -> None:
    response = logged_client.post(
        f"/api/properties/{prop['id']}/financings", json=financing_payload(**overrides)
    )

    assert response.status_code == 400
    assert field in [d["field"] for d in response.get_json()["details"]]


def test_first_installment_must_fall_on_due_day(logged_client: FlaskClient, prop: dict) -> None:
    url = f"/api/properties/{prop['id']}/financings"

    wrong = logged_client.post(url, json=financing_payload(first_installment_date="2024-01-15"))
    clamped = logged_client.post(
        url, json=financing_payload(due_day=31, first_installment_date="2024-04-30")
    )

    assert wrong.status_code == 400
    assert clamped.status_code == 201


# --- despesas ---


def test_expense_crud(logged_client: FlaskClient, prop: dict) -> None:
    expense = create_expense(logged_client, prop["id"])
    assert expense["amount_cents"] == 65_000
    assert expense["has_payments"] is False

    updated = logged_client.patch(f"/api/expenses/{expense['id']}", json={"due_day": 8})
    assert updated.status_code == 200
    assert updated.get_json()["due_day"] == 8

    assert logged_client.delete(f"/api/expenses/{expense['id']}").status_code == 204


def test_expense_end_before_start_returns_400(logged_client: FlaskClient, prop: dict) -> None:
    response = logged_client.post(
        f"/api/properties/{prop['id']}/expenses",
        json=expense_payload(start_date="2026-05-01", end_date="2026-04-30"),
    )

    assert response.status_code == 400


def test_patch_is_validated_with_the_stored_fields(logged_client: FlaskClient, prop: dict) -> None:
    expense = create_expense(logged_client, prop["id"], start_date="2026-05-01")

    response = logged_client.patch(
        f"/api/expenses/{expense['id']}", json={"end_date": "2026-04-01"}
    )

    assert response.status_code == 400


# --- travas da regra depois do 1º pagamento (ESCOPO 3.5) ---


@pytest.mark.parametrize(
    "change",
    [
        {"due_day": 6},
        {"frequency": "bimestral"},
        {"start_date": "2025-12-01"},
        {"installment_count": 12},
    ],
)
def test_expense_rule_is_locked_after_payment(
    logged_client: FlaskClient, prop: dict, change: dict
) -> None:
    expense = create_expense(logged_client, prop["id"])
    pay(logged_client, "recurring_expense", expense["id"], "2026-01-05")

    response = logged_client.patch(f"/api/expenses/{expense['id']}", json=change)

    assert response.status_code == 409
    body = response.get_json()
    assert body["error"] == "rule_locked_by_payments"
    assert body["fields"] == list(change)


def test_expense_other_fields_stay_editable_after_payment(
    logged_client: FlaskClient, prop: dict
) -> None:
    expense = create_expense(logged_client, prop["id"])
    pay(logged_client, "recurring_expense", expense["id"], "2026-01-05")

    response = logged_client.patch(
        f"/api/expenses/{expense['id']}",
        json={
            "description": "Condomínio reajustado",
            "amount_cents": 70_000,
            "end_date": "2026-12-31",
            "is_active": True,
            "due_day": 5,  # mesmo valor: não conta como mudança
        },
    )

    assert response.status_code == 200
    assert response.get_json()["has_payments"] is True


def test_financing_rule_is_locked_after_payment(logged_client: FlaskClient, prop: dict) -> None:
    financing = create_financing(logged_client, prop["id"])
    assert pay(logged_client, "financing", financing["id"], "2024-01-10").status_code == 201

    locked = logged_client.patch(
        f"/api/financings/{financing['id']}",
        json={"due_day": 15, "first_installment_date": "2024-01-15"},
    )
    editable = logged_client.patch(
        f"/api/financings/{financing['id']}", json={"is_paid_off": True, "term_months": 300}
    )

    assert locked.status_code == 409
    assert locked.get_json()["fields"] == ["due_day", "first_installment_date"]
    assert editable.status_code == 200


# --- 404 ---


@pytest.mark.parametrize(
    "url",
    ["/api/valuations/999", "/api/financings/999", "/api/balances/999", "/api/expenses/999"],
)
def test_unknown_record_returns_404(logged_client: FlaskClient, url: str) -> None:
    assert logged_client.patch(url, json={}).status_code == 404
    assert logged_client.delete(url).status_code == 404


@pytest.mark.parametrize("kind", ["valuations", "financings", "expenses"])
def test_create_under_unknown_property_returns_404(logged_client: FlaskClient, kind: str) -> None:
    assert logged_client.post(f"/api/properties/999/{kind}", json={}).status_code == 404


def test_create_balance_under_unknown_financing_returns_404(logged_client: FlaskClient) -> None:
    assert logged_client.post("/api/financings/999/balances", json={}).status_code == 404
