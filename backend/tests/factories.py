"""Criação de objetos válidos para testes, com defaults sobrescrevíveis."""

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import (
    DebtBalance,
    Financing,
    MarketValuation,
    Payment,
    Property,
    RecurringExpense,
    User,
)
from app.models.enums import (
    AmortizationSystem,
    ExpenseType,
    Frequency,
    InterestIndex,
    PropertyType,
    PropertyUsage,
    ValuationSource,
)


def _save[T](session: Session, obj: T) -> T:
    session.add(obj)
    session.flush()
    return obj


def make_user(session: Session, email: str = "dono@example.com") -> User:
    return _save(session, User(email=email, password_hash="hash-de-teste"))


def make_property(session: Session, user: User, **overrides: Any) -> Property:
    fields: dict[str, Any] = {
        "user_id": user.id,
        "nickname": "Apto Centro",
        "property_type": PropertyType.APARTAMENTO,
        "usage": PropertyUsage.MORADIA_PROPRIA,
    }
    return _save(session, Property(**(fields | overrides)))


def make_valuation(session: Session, prop: Property, **overrides: Any) -> MarketValuation:
    fields: dict[str, Any] = {
        "property_id": prop.id,
        "valuation_date": date(2026, 1, 1),
        "value": Decimal("400000.00"),
        "source": ValuationSource.ESTIMATIVA_PROPRIA,
    }
    return _save(session, MarketValuation(**(fields | overrides)))


def make_financing(session: Session, prop: Property, **overrides: Any) -> Financing:
    fields: dict[str, Any] = {
        "property_id": prop.id,
        "lender": "Banco X",
        "financed_amount": Decimal("300000.00"),
        "amortization_system": AmortizationSystem.SAC,
        "annual_interest_rate": Decimal("9.5"),
        "interest_index": InterestIndex.TR,
        "term_months": 360,
        "first_installment_date": date(2024, 1, 10),
        "due_day": 10,
        "current_installment": Decimal("2500.00"),
    }
    return _save(session, Financing(**(fields | overrides)))


def make_balance(session: Session, financing: Financing, **overrides: Any) -> DebtBalance:
    fields: dict[str, Any] = {
        "financing_id": financing.id,
        "balance_date": date(2026, 1, 1),
        "balance": Decimal("100000.00"),
    }
    return _save(session, DebtBalance(**(fields | overrides)))


def make_expense(session: Session, prop: Property, **overrides: Any) -> RecurringExpense:
    fields: dict[str, Any] = {
        "property_id": prop.id,
        "expense_type": ExpenseType.CONDOMINIO,
        "description": "Condomínio",
        "amount": Decimal("650.00"),
        "frequency": Frequency.MENSAL,
        "due_day": 5,
        "start_date": date(2026, 1, 1),
    }
    return _save(session, RecurringExpense(**(fields | overrides)))


def make_payment(session: Session, **fields: Any) -> Payment:
    defaults: dict[str, Any] = {
        "reference_due_date": date(2026, 1, 5),
        "payment_date": date(2026, 1, 5),
        "amount_paid": Decimal("650.00"),
    }
    return _save(session, Payment(**(defaults | fields)))
