from __future__ import annotations

from flask import Blueprint, jsonify
from sqlalchemy.exc import IntegrityError

from app.db import get_session
from app.models import Payment
from app.repositories.mappers import to_expense_rule, to_financing_rule
from app.repositories.owned import owned_expense, owned_financing, owned_payment, payment_exists
from app.routes.helpers import current_user_id, no_content, require
from app.schemas.common import api_to_orm, orm_to_api
from app.schemas.payments import PaymentCreateIn, PaymentUpdateIn
from app.serializers import payment_json
from app.services.dues import DueSource, SourceKind, expense_has_due_on, financing_has_due_on
from app.services.money import from_cents
from app.validation import RequestValidationError, parse_body, parse_patch

payments_bp = Blueprint("payments", __name__, url_prefix="/api/payments")


def _not_a_due_date() -> RequestValidationError:
    return RequestValidationError(
        [
            {
                "field": "reference_due_date",
                "type": "not_a_due_date",
                "message": "a data não corresponde a um vencimento desta despesa ou financiamento",
            }
        ]
    )


def _duplicate_response():
    return jsonify(error="payment_already_registered"), 409


def _check_source(data: PaymentCreateIn) -> None:
    """404 se a origem não é do usuário; 400 se a data não é um vencimento dela."""
    session, user_id = get_session(), current_user_id()
    if data.source_kind is SourceKind.RECURRING_EXPENSE:
        expense = require(owned_expense(session, user_id, data.source_id))
        is_due = expense_has_due_on(to_expense_rule(expense), data.reference_due_date)
    else:
        financing = require(owned_financing(session, user_id, data.source_id))
        is_due = financing_has_due_on(to_financing_rule(financing), data.reference_due_date)
    if not is_due:
        raise _not_a_due_date()


def _new_payment(data: PaymentCreateIn) -> Payment:
    is_expense = data.source_kind is SourceKind.RECURRING_EXPENSE
    return Payment(
        recurring_expense_id=data.source_id if is_expense else None,
        financing_id=None if is_expense else data.source_id,
        reference_due_date=data.reference_due_date,
        payment_date=data.payment_date,
        amount_paid=from_cents(data.amount_paid_cents),
    )


@payments_bp.post("")
def create_payment():
    data = parse_body(PaymentCreateIn)
    _check_source(data)
    session = get_session()
    source = DueSource(data.source_kind, data.source_id)
    if payment_exists(session, source, data.reference_due_date):
        return _duplicate_response()
    payment = _new_payment(data)
    session.add(payment)
    try:
        session.commit()
    except IntegrityError:
        # Dois registros simultâneos do mesmo vencimento: o UNIQUE do banco decide.
        session.rollback()
        return _duplicate_response()
    return jsonify(payment_json(payment)), 201


@payments_bp.patch("/<int:payment_id>")
def update_payment(payment_id: int):
    session = get_session()
    payment = require(owned_payment(session, current_user_id(), payment_id))
    api_to_orm(parse_patch(PaymentUpdateIn, orm_to_api(payment, PaymentUpdateIn)).new, payment)
    session.commit()
    return jsonify(payment_json(payment))


@payments_bp.delete("/<int:payment_id>")
def delete_payment(payment_id: int):
    session = get_session()
    session.delete(require(owned_payment(session, current_user_id(), payment_id)))
    session.commit()
    return no_content()
