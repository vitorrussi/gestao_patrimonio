"""Painel, compromissos do mês e vencimentos por período."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, jsonify

from app import clock
from app.db import get_session
from app.repositories.portfolio import Portfolio, load_portfolio
from app.routes.helpers import current_user_id
from app.schemas.common import cents_or_none
from app.schemas.views import MonthQuery, PeriodQuery
from app.serializers import portfolio_json
from app.services.dues import (
    DueWithStatus,
    MonthSummary,
    dues_in_period,
    month_commitments,
    summarize,
    with_status,
)
from app.services.equity import portfolio_summary
from app.services.money import to_cents
from app.validation import parse_query

views_bp = Blueprint("views", __name__, url_prefix="/api")


def _item_json(item: DueWithStatus, portfolio: Portfolio) -> dict[str, Any]:
    due = item.due
    label = portfolio.labels[due.source]
    return {
        "source_kind": due.source.kind.value,
        "source_id": due.source.source_id,
        "property_id": label.property_id,
        "property_nickname": label.property_nickname,
        "description": label.description,
        "due_date": due.due_date.isoformat(),
        "expected_amount_cents": to_cents(due.expected_amount),
        "status": item.status.value,
        "amount_paid_cents": cents_or_none(item.amount_paid),
        "payment_id": portfolio.payment_ids.get((due.source, due.due_date)),
    }


def _summary_json(summary: MonthSummary, portfolio: Portfolio) -> dict[str, Any]:
    return {
        "items": [_item_json(item, portfolio) for item in summary.items],
        "total_expected_cents": to_cents(summary.total_expected),
        "total_paid_cents": to_cents(summary.total_paid),
        "total_open_cents": to_cents(summary.total_open),
        "total_overdue_cents": to_cents(summary.total_overdue),
    }


@views_bp.get("/dashboard")
def dashboard():
    portfolio = load_portfolio(get_session(), current_user_id())
    return jsonify(portfolio_json(portfolio_summary(portfolio.property_inputs)))


@views_bp.get("/commitments")
def commitments():
    query = parse_query(MonthQuery)
    today = clock.today()
    year, month = (
        (query.year, query.month) if query.year and query.month else (today.year, today.month)
    )
    portfolio = load_portfolio(get_session(), current_user_id())
    summary = month_commitments(
        portfolio.expense_rules, portfolio.financing_rules, portfolio.payments, year, month, today
    )
    return jsonify(
        {
            "year": year,
            "month": month,
            "today": today.isoformat(),
            **_summary_json(summary, portfolio),
        }
    )


@views_bp.get("/dues")
def dues():
    query = parse_query(PeriodQuery)
    today = clock.today()
    portfolio = load_portfolio(get_session(), current_user_id())
    period_dues = dues_in_period(
        portfolio.expense_rules, portfolio.financing_rules, query.start, query.end
    )
    summary = summarize(with_status(period_dues, portfolio.payments, today))
    return jsonify(
        {
            "start": query.start.isoformat(),
            "end": query.end.isoformat(),
            "today": today.isoformat(),
            **_summary_json(summary, portfolio),
        }
    )
