import pytest
from flask.testing import FlaskClient

from tests.api_helpers import (
    create_balance,
    create_expense,
    create_financing,
    create_property,
    create_valuation,
    pay,
    property_payload,
)


def test_create_and_read_property(logged_client: FlaskClient) -> None:
    created = create_property(logged_client)

    detail = logged_client.get(f"/api/properties/{created['id']}").get_json()

    assert detail["nickname"] == "Apto Centro"
    assert detail["state"] == "SC"
    assert detail["zip_code"] == "89201-000"
    assert detail["ownership_percentage"] == "100.0000"
    assert detail["acquisition_date"] == "2020-05-10"
    assert detail["purchase_price_cents"] == 35_000_000
    assert detail["acquisition_total_cents"] == 36_050_000
    assert detail["is_active"] is True
    assert detail["market_value_cents"] is None
    assert detail["net_cents"] is None
    assert detail["debt_cents"] == 0
    assert detail["valuations"] == detail["financings"] == detail["expenses"] == []
    assert detail["payments"] == []


def test_minimal_property_uses_defaults(logged_client: FlaskClient) -> None:
    body = {"nickname": "Terreno Pirabeiraba", "property_type": "terreno", "usage": "vazio"}

    created = logged_client.post("/api/properties", json=body)

    assert created.status_code == 201
    data = created.get_json()
    assert data["ownership_percentage"] == "100.0000"
    assert data["purchase_price_cents"] == 0
    assert data["street"] is None


def test_list_shows_equity_per_property(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client, ownership_percentage="50")
    create_valuation(logged_client, prop["id"])
    financing = create_financing(logged_client, prop["id"])
    create_balance(logged_client, financing["id"])

    [item] = logged_client.get("/api/properties").get_json()

    assert item["market_value_cents"] == 40_000_000
    assert item["gross_cents"] == 20_000_000
    assert item["debt_cents"] == 10_000_000
    assert item["net_cents"] == 10_000_000
    assert item["debt_estimated"] is False
    assert item["ownership_percentage"] == "50.0000"


def test_detail_brings_everything_of_the_property(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client)
    create_valuation(logged_client, prop["id"], valuation_date="2025-01-01", value_cents=1)
    create_valuation(logged_client, prop["id"], valuation_date="2026-02-01", value_cents=2)
    financing = create_financing(logged_client, prop["id"])
    create_balance(logged_client, financing["id"])
    expense = create_expense(logged_client, prop["id"])
    assert pay(logged_client, "recurring_expense", expense["id"], "2026-01-05").status_code == 201

    detail = logged_client.get(f"/api/properties/{prop['id']}").get_json()

    assert [v["value_cents"] for v in detail["valuations"]] == [2, 1]  # mais recente primeiro
    assert detail["market_value_cents"] == 2
    assert detail["financings"][0]["current_debt_cents"] == 10_000_000
    assert len(detail["financings"][0]["balances"]) == 1
    assert detail["expenses"][0]["has_payments"] is True
    assert detail["financings"][0]["has_payments"] is False
    assert detail["payments"][0]["reference_due_date"] == "2026-01-05"


def test_patch_changes_only_sent_fields(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client)

    response = logged_client.patch(f"/api/properties/{prop['id']}", json={"nickname": "Apto Novo"})

    assert response.status_code == 200
    data = response.get_json()
    assert data["nickname"] == "Apto Novo"
    assert data["purchase_price_cents"] == 35_000_000
    assert data["city"] == "Joinville"


def test_mark_property_as_sold(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client)

    response = logged_client.patch(f"/api/properties/{prop['id']}", json={"is_active": False})

    assert response.get_json()["is_active"] is False
    assert logged_client.get("/api/properties").get_json()[0]["is_active"] is False


def test_delete_property_removes_it_and_its_records(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client)
    expense = create_expense(logged_client, prop["id"])

    assert logged_client.delete(f"/api/properties/{prop['id']}").status_code == 204
    assert logged_client.get(f"/api/properties/{prop['id']}").status_code == 404
    assert logged_client.delete(f"/api/expenses/{expense['id']}").status_code == 404


@pytest.mark.parametrize(
    ("overrides", "field"),
    [
        ({"nickname": "   "}, "nickname"),
        ({"property_type": "castelo"}, "property_type"),
        ({"state": "Santa Catarina"}, "state"),
        ({"zip_code": "123"}, "zip_code"),
        ({"ownership_percentage": "100.5"}, "ownership_percentage"),
        ({"ownership_percentage": "33.33333"}, "ownership_percentage"),
        ({"ownership_percentage": 50.5}, "ownership_percentage"),
        ({"purchase_price_cents": 100.5}, "purchase_price_cents"),
        ({"purchase_price_cents": "100"}, "purchase_price_cents"),
        ({"purchase_price_cents": -1}, "purchase_price_cents"),
        ({"acquisition_date": "10/05/2020"}, "acquisition_date"),
        ({"is_active": "sim"}, "is_active"),
        ({"user_id": 999}, "user_id"),
    ],
)
def test_invalid_property_returns_400(
    logged_client: FlaskClient, overrides: dict, field: str
) -> None:
    response = logged_client.post("/api/properties", json=property_payload(**overrides))

    assert response.status_code == 400
    assert field in [d["field"] for d in response.get_json()["details"]]


def test_invalid_patch_returns_400_and_changes_nothing(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client)

    response = logged_client.patch(
        f"/api/properties/{prop['id']}", json={"nickname": "Outro", "state": "XXX"}
    )

    assert response.status_code == 400
    assert (
        logged_client.get(f"/api/properties/{prop['id']}").get_json()["nickname"] == "Apto Centro"
    )


def test_patch_with_non_object_body_returns_400(logged_client: FlaskClient) -> None:
    prop = create_property(logged_client)

    response = logged_client.patch(f"/api/properties/{prop['id']}", json=["nickname"])

    assert response.status_code == 400
    assert response.get_json()["details"][0]["type"] == "json_object_required"


def test_unknown_property_returns_404(logged_client: FlaskClient) -> None:
    assert logged_client.get("/api/properties/999").status_code == 404
    assert logged_client.patch("/api/properties/999", json={}).status_code == 404
    assert logged_client.delete("/api/properties/999").status_code == 404
