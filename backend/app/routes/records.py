"""Avaliações, financiamentos, saldos devedores e despesas.

Cria-se pelo registro pai (imóvel ou financiamento); edita-se e exclui-se pelo próprio id.
A leitura é pela ficha do imóvel.
"""

from __future__ import annotations

from flask import Blueprint, jsonify

from app.db import get_session
from app.models import DebtBalance, Financing, MarketValuation, RecurringExpense
from app.repositories.owned import (
    owned_balance,
    owned_expense,
    owned_financing,
    owned_property,
    owned_valuation,
    source_has_payments,
)
from app.routes.helpers import current_user_id, no_content, require, rule_locked_response
from app.schemas.children import (
    EXPENSE_RULE_FIELDS,
    FINANCING_RULE_FIELDS,
    BalanceIn,
    ExpenseIn,
    FinancingIn,
    ValuationIn,
)
from app.schemas.common import api_to_orm, orm_to_api
from app.serializers import balance_json, expense_json, financing_json, valuation_json
from app.services.dues import DueSource, SourceKind
from app.validation import parse_body, parse_patch

records_bp = Blueprint("records", __name__, url_prefix="/api")


def _save(obj: object) -> None:
    session = get_session()
    session.add(obj)
    session.commit()


def _delete(obj: object) -> tuple[str, int]:
    session = get_session()
    session.delete(obj)
    session.commit()
    return no_content()


def _has_payments(kind: SourceKind, source_id: int) -> bool:
    return source_has_payments(get_session(), DueSource(kind, source_id))


# --- avaliações ---


@records_bp.post("/properties/<int:property_id>/valuations")
def create_valuation(property_id: int):
    prop = require(owned_property(get_session(), current_user_id(), property_id))
    valuation = MarketValuation(property_id=prop.id)
    api_to_orm(parse_body(ValuationIn), valuation)
    _save(valuation)
    return jsonify(valuation_json(valuation)), 201


@records_bp.patch("/valuations/<int:valuation_id>")
def update_valuation(valuation_id: int):
    valuation = require(owned_valuation(get_session(), current_user_id(), valuation_id))
    api_to_orm(parse_patch(ValuationIn, orm_to_api(valuation, ValuationIn)).new, valuation)
    _save(valuation)
    return jsonify(valuation_json(valuation))


@records_bp.delete("/valuations/<int:valuation_id>")
def delete_valuation(valuation_id: int):
    return _delete(require(owned_valuation(get_session(), current_user_id(), valuation_id)))


# --- financiamentos ---


@records_bp.post("/properties/<int:property_id>/financings")
def create_financing(property_id: int):
    prop = require(owned_property(get_session(), current_user_id(), property_id))
    financing = Financing(property_id=prop.id)
    api_to_orm(parse_body(FinancingIn), financing)
    _save(financing)
    return jsonify(financing_json(financing, has_payments=False)), 201


@records_bp.patch("/financings/<int:financing_id>")
def update_financing(financing_id: int):
    financing = require(owned_financing(get_session(), current_user_id(), financing_id))
    patch = parse_patch(FinancingIn, orm_to_api(financing, FinancingIn))
    has_payments = _has_payments(SourceKind.FINANCING, financing.id)
    locked = patch.changed & FINANCING_RULE_FIELDS
    if locked and has_payments:
        return rule_locked_response(locked)
    api_to_orm(patch.new, financing)
    _save(financing)
    return jsonify(financing_json(financing, has_payments))


@records_bp.delete("/financings/<int:financing_id>")
def delete_financing(financing_id: int):
    return _delete(require(owned_financing(get_session(), current_user_id(), financing_id)))


# --- saldos devedores ---


@records_bp.post("/financings/<int:financing_id>/balances")
def create_balance(financing_id: int):
    financing = require(owned_financing(get_session(), current_user_id(), financing_id))
    balance = DebtBalance(financing_id=financing.id)
    api_to_orm(parse_body(BalanceIn), balance)
    _save(balance)
    return jsonify(balance_json(balance)), 201


@records_bp.patch("/balances/<int:balance_id>")
def update_balance(balance_id: int):
    balance = require(owned_balance(get_session(), current_user_id(), balance_id))
    api_to_orm(parse_patch(BalanceIn, orm_to_api(balance, BalanceIn)).new, balance)
    _save(balance)
    return jsonify(balance_json(balance))


@records_bp.delete("/balances/<int:balance_id>")
def delete_balance(balance_id: int):
    return _delete(require(owned_balance(get_session(), current_user_id(), balance_id)))


# --- despesas recorrentes ---


@records_bp.post("/properties/<int:property_id>/expenses")
def create_expense(property_id: int):
    prop = require(owned_property(get_session(), current_user_id(), property_id))
    expense = RecurringExpense(property_id=prop.id)
    api_to_orm(parse_body(ExpenseIn), expense)
    _save(expense)
    return jsonify(expense_json(expense, has_payments=False)), 201


@records_bp.patch("/expenses/<int:expense_id>")
def update_expense(expense_id: int):
    expense = require(owned_expense(get_session(), current_user_id(), expense_id))
    patch = parse_patch(ExpenseIn, orm_to_api(expense, ExpenseIn))
    has_payments = _has_payments(SourceKind.RECURRING_EXPENSE, expense.id)
    locked = patch.changed & EXPENSE_RULE_FIELDS
    if locked and has_payments:
        return rule_locked_response(locked)
    api_to_orm(patch.new, expense)
    _save(expense)
    return jsonify(expense_json(expense, has_payments))


@records_bp.delete("/expenses/<int:expense_id>")
def delete_expense(expense_id: int):
    return _delete(require(owned_expense(get_session(), current_user_id(), expense_id)))
