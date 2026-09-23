"""Buscas por id que só encontram registros do usuário informado (regra 2).

Todas passam pelo imóvel dono do registro. Registro de outro usuário = None (vira 404).
"""

from __future__ import annotations

from datetime import date

from sqlalchemy import Select, exists, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    DebtBalance,
    Financing,
    MarketValuation,
    Payment,
    Property,
    RecurringExpense,
)
from app.services.dues import DueSource, SourceKind


def _user_expense_ids(user_id: int) -> Select[tuple[int]]:
    return (
        select(RecurringExpense.id)
        .join(RecurringExpense.property)
        .where(Property.user_id == user_id)
    )


def _user_financing_ids(user_id: int) -> Select[tuple[int]]:
    return select(Financing.id).join(Financing.property).where(Property.user_id == user_id)


def _user_payments_filter(user_id: int):
    return or_(
        Payment.recurring_expense_id.in_(_user_expense_ids(user_id)),
        Payment.financing_id.in_(_user_financing_ids(user_id)),
    )


def owned_property(session: Session, user_id: int, property_id: int) -> Property | None:
    return session.scalar(
        select(Property).where(Property.id == property_id, Property.user_id == user_id)
    )


def owned_valuation(session: Session, user_id: int, valuation_id: int) -> MarketValuation | None:
    return session.scalar(
        select(MarketValuation)
        .join(MarketValuation.property)
        .where(MarketValuation.id == valuation_id, Property.user_id == user_id)
    )


def owned_financing(session: Session, user_id: int, financing_id: int) -> Financing | None:
    return session.scalar(
        select(Financing)
        .join(Financing.property)
        .where(Financing.id == financing_id, Property.user_id == user_id)
    )


def owned_balance(session: Session, user_id: int, balance_id: int) -> DebtBalance | None:
    return session.scalar(
        select(DebtBalance)
        .join(DebtBalance.financing)
        .join(Financing.property)
        .where(DebtBalance.id == balance_id, Property.user_id == user_id)
    )


def owned_expense(session: Session, user_id: int, expense_id: int) -> RecurringExpense | None:
    return session.scalar(
        select(RecurringExpense)
        .join(RecurringExpense.property)
        .where(RecurringExpense.id == expense_id, Property.user_id == user_id)
    )


def owned_payment(session: Session, user_id: int, payment_id: int) -> Payment | None:
    return session.scalar(
        select(Payment).where(Payment.id == payment_id, _user_payments_filter(user_id))
    )


def user_properties(session: Session, user_id: int) -> list[Property]:
    """Imóveis do usuário com avaliações, financiamentos (e saldos) e despesas já carregados."""
    statement = (
        select(Property)
        .where(Property.user_id == user_id)
        .options(
            selectinload(Property.valuations),
            selectinload(Property.financings).selectinload(Financing.balances),
            selectinload(Property.expenses),
        )
        .order_by(Property.nickname, Property.id)
    )
    return list(session.scalars(statement))


def user_payments(session: Session, user_id: int) -> list[Payment]:
    statement = (
        select(Payment)
        .where(_user_payments_filter(user_id))
        .order_by(Payment.reference_due_date, Payment.id)
    )
    return list(session.scalars(statement))


def property_payments(session: Session, prop: Property) -> list[Payment]:
    expense_ids = select(RecurringExpense.id).where(RecurringExpense.property_id == prop.id)
    financing_ids = select(Financing.id).where(Financing.property_id == prop.id)
    statement = (
        select(Payment)
        .where(
            or_(
                Payment.recurring_expense_id.in_(expense_ids),
                Payment.financing_id.in_(financing_ids),
            )
        )
        .order_by(Payment.reference_due_date, Payment.id)
    )
    return list(session.scalars(statement))


def _source_column(source: DueSource):
    if source.kind is SourceKind.RECURRING_EXPENSE:
        return Payment.recurring_expense_id
    return Payment.financing_id


def source_has_payments(session: Session, source: DueSource) -> bool:
    return bool(session.scalar(select(exists().where(_source_column(source) == source.source_id))))


def payment_exists(session: Session, source: DueSource, reference_due_date: date) -> bool:
    condition = (_source_column(source) == source.source_id) & (
        Payment.reference_due_date == reference_due_date
    )
    return bool(session.scalar(select(exists().where(condition))))
