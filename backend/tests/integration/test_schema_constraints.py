"""Regras garantidas pelo banco, testadas sobre o schema criado pelas migrações."""

from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import create_engine_with_pragmas, make_session_factory
from app.models import MarketValuation, Payment, Property, RecurringExpense, User
from tests.factories import (
    make_balance,
    make_expense,
    make_financing,
    make_payment,
    make_property,
    make_user,
    make_valuation,
)
from tests.migrations_helpers import upgrade_to_head


@pytest.fixture()
def session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Session]:
    engine = create_engine_with_pragmas(upgrade_to_head(tmp_path, monkeypatch))
    with make_session_factory(engine)() as db_session:
        yield db_session
    engine.dispose()


@pytest.fixture()
def prop(session: Session) -> Property:
    return make_property(session, make_user(session))


def _count(session: Session, model: type) -> int:
    return session.scalar(select(func.count()).select_from(model)) or 0


def test_money_and_percentages_are_integers_in_the_database(
    session: Session, prop: Property
) -> None:
    prop.purchase_price = Decimal("350000.10")
    prop.ownership_percentage = Decimal("33.3333")
    session.flush()

    row = session.execute(
        text(
            "SELECT purchase_price_cents, typeof(purchase_price_cents), "
            "ownership_percentage_x10000 FROM properties"
        )
    ).one()

    assert tuple(row) == (35000010, "integer", 333333)
    session.expire_all()
    assert session.get_one(Property, prop.id).purchase_price == Decimal("350000.10")


def test_default_ownership_is_100_percent(session: Session, prop: Property) -> None:
    session.expire_all()
    assert session.get_one(Property, prop.id).ownership_percentage == Decimal("100")


def test_duplicate_payment_for_same_expense_and_date_is_rejected(
    session: Session, prop: Property
) -> None:
    expense = make_expense(session, prop)
    make_payment(session, recurring_expense_id=expense.id)

    with pytest.raises(IntegrityError):
        make_payment(session, recurring_expense_id=expense.id, amount_paid=Decimal("1.00"))


def test_duplicate_payment_for_same_financing_and_date_is_rejected(
    session: Session, prop: Property
) -> None:
    financing = make_financing(session, prop)
    make_payment(session, financing_id=financing.id, reference_due_date=date(2026, 1, 10))

    with pytest.raises(IntegrityError):
        make_payment(session, financing_id=financing.id, reference_due_date=date(2026, 1, 10))


def test_same_date_for_different_sources_is_allowed(session: Session, prop: Property) -> None:
    expense = make_expense(session, prop)
    other_expense = make_expense(session, prop, description="IPTU")
    financing = make_financing(session, prop)
    same_date = date(2026, 1, 5)

    make_payment(session, recurring_expense_id=expense.id, reference_due_date=same_date)
    make_payment(session, recurring_expense_id=other_expense.id, reference_due_date=same_date)
    make_payment(session, financing_id=financing.id, reference_due_date=same_date)

    assert _count(session, Payment) == 3


def test_payment_needs_exactly_one_source(session: Session, prop: Property) -> None:
    expense = make_expense(session, prop)
    financing = make_financing(session, prop)

    with pytest.raises(IntegrityError):
        make_payment(session)
    session.rollback()

    with pytest.raises(IntegrityError):
        make_payment(session, recurring_expense_id=expense.id, financing_id=financing.id)


@pytest.mark.parametrize("due_day", [0, 32])
def test_due_day_outside_1_31_is_rejected(session: Session, prop: Property, due_day: int) -> None:
    with pytest.raises(IntegrityError):
        make_expense(session, prop, due_day=due_day)


@pytest.mark.parametrize("due_day", [1, 31])
def test_due_day_limits_are_accepted(session: Session, prop: Property, due_day: int) -> None:
    make_financing(session, prop, due_day=due_day)


def test_ownership_above_100_is_rejected(session: Session) -> None:
    user = make_user(session)

    with pytest.raises(IntegrityError):
        make_property(session, user, ownership_percentage=Decimal("100.0001"))


def test_negative_money_is_rejected(session: Session, prop: Property) -> None:
    with pytest.raises(IntegrityError):
        make_valuation(session, prop, value=Decimal("-0.01"))


def test_end_date_before_start_is_rejected(session: Session, prop: Property) -> None:
    with pytest.raises(IntegrityError):
        make_expense(session, prop, start_date=date(2026, 5, 1), end_date=date(2026, 4, 30))


def test_zero_installments_is_rejected(session: Session, prop: Property) -> None:
    with pytest.raises(IntegrityError):
        make_expense(session, prop, installment_count=0)


def test_enum_value_outside_scope_is_rejected_by_the_database(
    session: Session, prop: Property
) -> None:
    with pytest.raises(IntegrityError):
        session.execute(
            text("UPDATE properties SET usage = 'invalido' WHERE id = :id"), {"id": prop.id}
        )


def test_foreign_keys_are_enforced(session: Session) -> None:
    with pytest.raises(IntegrityError):
        session.execute(
            text(
                "INSERT INTO market_valuations (property_id, valuation_date, value_cents, source) "
                "VALUES (999, '2026-01-01', 100, 'laudo')"
            )
        )


def test_deleting_property_cascades_to_everything(session: Session, prop: Property) -> None:
    make_valuation(session, prop)
    financing = make_financing(session, prop)
    make_balance(session, financing)
    expense = make_expense(session, prop)
    make_payment(session, recurring_expense_id=expense.id)
    make_payment(session, financing_id=financing.id, reference_due_date=date(2026, 1, 10))

    session.execute(text("DELETE FROM properties WHERE id = :id"), {"id": prop.id})

    for table in (
        "market_valuations",
        "financings",
        "debt_balances",
        "recurring_expenses",
        "payments",
    ):
        assert session.scalar(text(f"SELECT count(*) FROM {table}")) == 0


def test_deleting_user_cascades_to_properties(session: Session, prop: Property) -> None:
    session.execute(text("DELETE FROM users"))

    assert _count(session, Property) == 0
    assert _count(session, User) == 0


def test_orm_delete_of_property_removes_children(session: Session, prop: Property) -> None:
    make_valuation(session, prop)
    make_expense(session, prop)

    session.delete(prop)
    session.flush()

    assert _count(session, MarketValuation) == 0
    assert _count(session, RecurringExpense) == 0
