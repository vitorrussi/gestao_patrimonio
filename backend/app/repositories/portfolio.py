"""Carrega tudo do usuário que os cálculos de painel e vencimentos precisam."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from sqlalchemy.orm import Session

from app.models import Property
from app.repositories.mappers import (
    payment_source,
    to_expense_rule,
    to_financing_rule,
    to_payment_record,
    to_property_input,
)
from app.repositories.owned import user_payments, user_properties
from app.services.dues import DueSource, ExpenseRule, FinancingRule, PaymentRecord, SourceKind
from app.services.equity import PropertyInput


@dataclass(frozen=True)
class SourceLabel:
    property_id: int
    property_nickname: str
    description: str


@dataclass
class Portfolio:
    properties: list[Property]
    property_inputs: list[PropertyInput] = field(default_factory=list)
    expense_rules: list[ExpenseRule] = field(default_factory=list)
    financing_rules: list[FinancingRule] = field(default_factory=list)
    payments: list[PaymentRecord] = field(default_factory=list)
    labels: dict[DueSource, SourceLabel] = field(default_factory=dict)
    payment_ids: dict[tuple[DueSource, date], int] = field(default_factory=dict)


def _add_property(portfolio: Portfolio, prop: Property) -> None:
    portfolio.property_inputs.append(to_property_input(prop))
    for expense in prop.expenses:
        portfolio.expense_rules.append(to_expense_rule(expense, prop.is_active))
        source = DueSource(SourceKind.RECURRING_EXPENSE, expense.id)
        portfolio.labels[source] = SourceLabel(prop.id, prop.nickname, expense.description)
    for financing in prop.financings:
        portfolio.financing_rules.append(to_financing_rule(financing, prop.is_active))
        source = DueSource(SourceKind.FINANCING, financing.id)
        description = f"Parcela do financiamento — {financing.lender}"
        portfolio.labels[source] = SourceLabel(prop.id, prop.nickname, description)


def load_portfolio(session: Session, user_id: int) -> Portfolio:
    portfolio = Portfolio(properties=user_properties(session, user_id))
    for prop in portfolio.properties:
        _add_property(portfolio, prop)
    for payment in user_payments(session, user_id):
        portfolio.payments.append(to_payment_record(payment))
        portfolio.payment_ids[(payment_source(payment), payment.reference_due_date)] = payment.id
    return portfolio
