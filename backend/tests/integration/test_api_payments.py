import pytest
from flask.testing import FlaskClient

from tests.api_helpers import create_expense, create_financing, create_property, pay


@pytest.fixture()
def expense(logged_client: FlaskClient) -> dict:
    return create_expense(logged_client, create_property(logged_client)["id"])


def test_register_payment(logged_client: FlaskClient, expense: dict) -> None:
    response = pay(
        logged_client, "recurring_expense", expense["id"], "2026-03-05", 67_210, "2026-03-07"
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["source_kind"] == "recurring_expense"
    assert body["source_id"] == expense["id"]
    assert body["reference_due_date"] == "2026-03-05"
    assert body["payment_date"] == "2026-03-07"
    assert body["amount_paid_cents"] == 67_210


def test_duplicate_payment_for_same_source_and_date_returns_409(
    logged_client: FlaskClient, expense: dict
) -> None:
    first = pay(logged_client, "recurring_expense", expense["id"], "2026-03-05")
    second = pay(logged_client, "recurring_expense", expense["id"], "2026-03-05", 1)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.get_json() == {"error": "payment_already_registered"}


def test_same_date_other_due_or_other_source_is_accepted(
    logged_client: FlaskClient, expense: dict
) -> None:
    other = create_expense(logged_client, expense["property_id"], description="Outra")

    assert pay(logged_client, "recurring_expense", expense["id"], "2026-03-05").status_code == 201
    assert pay(logged_client, "recurring_expense", expense["id"], "2026-04-05").status_code == 201
    assert pay(logged_client, "recurring_expense", other["id"], "2026-03-05").status_code == 201


def test_date_that_is_not_a_due_returns_400(logged_client: FlaskClient, expense: dict) -> None:
    response = pay(logged_client, "recurring_expense", expense["id"], "2026-03-06")

    assert response.status_code == 400
    assert response.get_json()["details"][0]["type"] == "not_a_due_date"


def test_date_before_start_is_not_a_due(logged_client: FlaskClient, expense: dict) -> None:
    assert pay(logged_client, "recurring_expense", expense["id"], "2025-12-05").status_code == 400


def test_financing_installment_payment(logged_client: FlaskClient) -> None:
    financing = create_financing(logged_client, create_property(logged_client)["id"])

    ok = pay(logged_client, "financing", financing["id"], "2026-09-10", 250_000)
    not_due = pay(logged_client, "financing", financing["id"], "2026-09-11", 250_000)
    after_term = pay(logged_client, "financing", financing["id"], "2054-01-10", 250_000)

    assert ok.status_code == 201
    assert not_due.status_code == 400
    assert after_term.status_code == 400  # 360 parcelas a partir de jan/2024 vão até dez/2053


def test_old_due_of_inactive_expense_or_paid_off_financing_can_still_be_paid(
    logged_client: FlaskClient, expense: dict
) -> None:
    financing = create_financing(logged_client, expense["property_id"])
    logged_client.patch(f"/api/expenses/{expense['id']}", json={"is_active": False})
    logged_client.patch(f"/api/financings/{financing['id']}", json={"is_paid_off": True})

    assert pay(logged_client, "recurring_expense", expense["id"], "2026-01-05").status_code == 201
    assert pay(logged_client, "financing", financing["id"], "2024-02-10").status_code == 201


def test_update_payment_date_and_amount(logged_client: FlaskClient, expense: dict) -> None:
    payment = pay(logged_client, "recurring_expense", expense["id"], "2026-03-05").get_json()

    response = logged_client.patch(
        f"/api/payments/{payment['id']}",
        json={"payment_date": "2026-03-09", "amount_paid_cents": 1},
    )

    assert response.status_code == 200
    assert response.get_json()["payment_date"] == "2026-03-09"
    assert response.get_json()["amount_paid_cents"] == 1
    assert response.get_json()["reference_due_date"] == "2026-03-05"


def test_reference_date_cannot_be_patched(logged_client: FlaskClient, expense: dict) -> None:
    payment = pay(logged_client, "recurring_expense", expense["id"], "2026-03-05").get_json()

    response = logged_client.patch(
        f"/api/payments/{payment['id']}", json={"reference_due_date": "2026-04-05"}
    )

    assert response.status_code == 400


def test_delete_payment_allows_registering_again(logged_client: FlaskClient, expense: dict) -> None:
    payment = pay(logged_client, "recurring_expense", expense["id"], "2026-03-05").get_json()

    assert logged_client.delete(f"/api/payments/{payment['id']}").status_code == 204
    assert pay(logged_client, "recurring_expense", expense["id"], "2026-03-05").status_code == 201


@pytest.mark.parametrize(
    ("changes", "field"),
    [
        ({"source_kind": "aluguel"}, "source_kind"),
        ({"amount_paid_cents": 650.0}, "amount_paid_cents"),
        ({"source_id": "1"}, "source_id"),
        ({"reference_due_date": "05/03/2026"}, "reference_due_date"),
    ],
)
def test_invalid_payment_returns_400(
    logged_client: FlaskClient, expense: dict, changes: dict, field: str
) -> None:
    body = {
        "source_kind": "recurring_expense",
        "source_id": expense["id"],
        "reference_due_date": "2026-03-05",
        "payment_date": "2026-03-05",
        "amount_paid_cents": 65_000,
    } | changes

    response = logged_client.post("/api/payments", json=body)

    assert response.status_code == 400
    assert field in [d["field"] for d in response.get_json()["details"]]


def test_unknown_source_or_payment_returns_404(logged_client: FlaskClient) -> None:
    assert pay(logged_client, "recurring_expense", 999, "2026-03-05").status_code == 404
    assert pay(logged_client, "financing", 999, "2026-03-05").status_code == 404
    assert logged_client.patch("/api/payments/999", json={}).status_code == 404
    assert logged_client.delete("/api/payments/999").status_code == 404
