"""Montagem das respostas JSON (dinheiro em centavos inteiros, datas ISO)."""

from __future__ import annotations

from typing import Any

from app.models import DebtBalance, Financing, MarketValuation, Payment, Property, RecurringExpense
from app.repositories.mappers import payment_source, to_financing_debt, to_property_input
from app.schemas.children import BalanceIn, ExpenseIn, FinancingIn, ValuationIn
from app.schemas.common import cents_or_none, orm_to_api
from app.schemas.payments import PaymentUpdateIn
from app.schemas.properties import PropertyIn
from app.services.dues import DueSource, SourceKind
from app.services.equity import (
    PortfolioSummary,
    PropertyEquity,
    acquisition_total,
    financing_debt,
    property_equity,
)
from app.services.money import to_cents


def equity_json(equity: PropertyEquity) -> dict[str, Any]:
    return {
        "market_value_cents": cents_or_none(equity.market_value),
        "gross_cents": cents_or_none(equity.gross),
        "debt_cents": to_cents(equity.debt),
        "net_cents": cents_or_none(equity.net),
        "debt_estimated": equity.debt_estimated,
    }


def property_summary_json(prop: Property) -> dict[str, Any]:
    """Item da lista de imóveis."""
    return {
        "id": prop.id,
        "nickname": prop.nickname,
        "property_type": prop.property_type.value,
        "usage": prop.usage.value,
        "is_active": prop.is_active,
        "ownership_percentage": str(prop.ownership_percentage),
        **equity_json(property_equity(to_property_input(prop))),
    }


def valuation_json(valuation: MarketValuation) -> dict[str, Any]:
    return {
        "id": valuation.id,
        "property_id": valuation.property_id,
        **orm_to_api(valuation, ValuationIn),
    }


def balance_json(balance: DebtBalance) -> dict[str, Any]:
    return {
        "id": balance.id,
        "financing_id": balance.financing_id,
        **orm_to_api(balance, BalanceIn),
    }


def financing_json(financing: Financing, has_payments: bool) -> dict[str, Any]:
    debt = financing_debt(to_financing_debt(financing))
    balances = sorted(financing.balances, key=lambda b: (b.balance_date, b.id), reverse=True)
    return {
        "id": financing.id,
        "property_id": financing.property_id,
        **orm_to_api(financing, FinancingIn),
        "current_debt_cents": to_cents(debt.amount),
        "debt_estimated": debt.estimated,
        "has_payments": has_payments,
        "balances": [balance_json(b) for b in balances],
    }


def expense_json(expense: RecurringExpense, has_payments: bool) -> dict[str, Any]:
    return {
        "id": expense.id,
        "property_id": expense.property_id,
        **orm_to_api(expense, ExpenseIn),
        "has_payments": has_payments,
    }


def payment_json(payment: Payment) -> dict[str, Any]:
    source = payment_source(payment)
    return {
        "id": payment.id,
        "source_kind": source.kind.value,
        "source_id": source.source_id,
        "reference_due_date": payment.reference_due_date.isoformat(),
        **orm_to_api(payment, PaymentUpdateIn),
    }


def property_detail_json(prop: Property, payments: list[Payment]) -> dict[str, Any]:
    """Ficha do imóvel: dados, valores, financiamentos, despesas e pagamentos."""
    paid_sources = {payment_source(p) for p in payments}
    summary = property_summary_json(prop)
    valuations = sorted(prop.valuations, key=lambda v: (v.valuation_date, v.id), reverse=True)
    return {
        **summary,
        **orm_to_api(prop, PropertyIn),
        "acquisition_total_cents": to_cents(
            acquisition_total(prop.purchase_price, prop.itbi, prop.deed_registration)
        ),
        "valuations": [valuation_json(v) for v in valuations],
        "financings": [
            financing_json(f, DueSource(SourceKind.FINANCING, f.id) in paid_sources)
            for f in prop.financings
        ],
        "expenses": [
            expense_json(e, DueSource(SourceKind.RECURRING_EXPENSE, e.id) in paid_sources)
            for e in prop.expenses
        ],
        "payments": [payment_json(p) for p in payments],
    }


def portfolio_json(summary: PortfolioSummary) -> dict[str, Any]:
    return {
        "gross_total_cents": to_cents(summary.gross_total),
        "debt_total_cents": to_cents(summary.debt_total),
        "net_total_cents": to_cents(summary.net_total),
        "property_count": summary.property_count,
        "count_by_type": {kind.value: n for kind, n in summary.count_by_type.items()},
        "properties_without_value": summary.properties_without_value,
        "debt_estimated": summary.debt_estimated,
    }
