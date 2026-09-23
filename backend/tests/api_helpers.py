"""Payloads válidos e atalhos de criação via API para os testes de integração."""

from typing import Any

from flask.testing import FlaskClient


def property_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "nickname": "Apto Centro",
        "property_type": "apartamento",
        "usage": "moradia_propria",
        "city": "Joinville",
        "state": "sc",
        "zip_code": "89201000",
        "ownership_percentage": "100",
        "acquisition_date": "2020-05-10",
        "acquisition_method": "compra",
        "purchase_price_cents": 35_000_000,
        "itbi_cents": 700_000,
        "deed_registration_cents": 350_000,
    } | overrides


def valuation_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "valuation_date": "2026-01-15",
        "value_cents": 40_000_000,
        "source": "corretor",
    } | overrides


def financing_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "lender": "Caixa",
        "contract_number": "8.4444.0001",
        "financed_amount_cents": 28_000_000,
        "amortization_system": "sac",
        "annual_interest_rate": "9.5",
        "interest_index": "tr",
        "term_months": 360,
        "first_installment_date": "2024-01-10",
        "due_day": 10,
        "current_installment_cents": 250_000,
    } | overrides


def balance_payload(**overrides: Any) -> dict[str, Any]:
    return {"balance_date": "2026-08-31", "balance_cents": 10_000_000} | overrides


def expense_payload(**overrides: Any) -> dict[str, Any]:
    return {
        "expense_type": "condominio",
        "description": "Condomínio",
        "amount_cents": 65_000,
        "frequency": "mensal",
        "due_day": 5,
        "start_date": "2026-01-01",
    } | overrides


def created(response: Any) -> dict[str, Any]:
    assert response.status_code == 201, response.get_json()
    return response.get_json()


def create_property(client: FlaskClient, **overrides: Any) -> dict[str, Any]:
    return created(client.post("/api/properties", json=property_payload(**overrides)))


def create_valuation(client: FlaskClient, property_id: int, **overrides: Any) -> dict[str, Any]:
    url = f"/api/properties/{property_id}/valuations"
    return created(client.post(url, json=valuation_payload(**overrides)))


def create_financing(client: FlaskClient, property_id: int, **overrides: Any) -> dict[str, Any]:
    url = f"/api/properties/{property_id}/financings"
    return created(client.post(url, json=financing_payload(**overrides)))


def create_balance(client: FlaskClient, financing_id: int, **overrides: Any) -> dict[str, Any]:
    url = f"/api/financings/{financing_id}/balances"
    return created(client.post(url, json=balance_payload(**overrides)))


def create_expense(client: FlaskClient, property_id: int, **overrides: Any) -> dict[str, Any]:
    url = f"/api/properties/{property_id}/expenses"
    return created(client.post(url, json=expense_payload(**overrides)))


def pay(
    client: FlaskClient,
    kind: str,
    source_id: int,
    reference: str,
    amount_cents: int = 65_000,
    payment_date: str | None = None,
):
    return client.post(
        "/api/payments",
        json={
            "source_kind": kind,
            "source_id": source_id,
            "reference_due_date": reference,
            "payment_date": payment_date or reference,
            "amount_paid_cents": amount_cents,
        },
    )
