"""ORM -> dataclasses dos services (que não conhecem o banco)."""

from __future__ import annotations

from app.models import Financing, Payment, Property, RecurringExpense
from app.services.dues import DueSource, ExpenseRule, FinancingRule, PaymentRecord, SourceKind
from app.services.equity import (
    BalanceRecord,
    FinancingDebtInput,
    PropertyInput,
    ValuationRecord,
)


def to_financing_debt(financing: Financing) -> FinancingDebtInput:
    return FinancingDebtInput(
        financed_amount=financing.financed_amount,
        is_paid_off=financing.is_paid_off,
        balances=[BalanceRecord(b.balance_date, b.balance, b.id) for b in financing.balances],
    )


def to_property_input(prop: Property) -> PropertyInput:
    return PropertyInput(
        property_id=prop.id,
        property_type=prop.property_type,
        ownership_percentage=prop.ownership_percentage,
        is_active=prop.is_active,
        valuations=[ValuationRecord(v.valuation_date, v.value, v.id) for v in prop.valuations],
        financings=[to_financing_debt(f) for f in prop.financings],
    )


def to_expense_rule(expense: RecurringExpense, property_is_active: bool = True) -> ExpenseRule:
    return ExpenseRule(
        expense_id=expense.id,
        property_id=expense.property_id,
        amount=expense.amount,
        frequency=expense.frequency,
        due_day=expense.due_day,
        start_date=expense.start_date,
        end_date=expense.end_date,
        installment_count=expense.installment_count,
        is_active=expense.is_active,
        property_is_active=property_is_active,
    )


def to_financing_rule(financing: Financing, property_is_active: bool = True) -> FinancingRule:
    return FinancingRule(
        financing_id=financing.id,
        property_id=financing.property_id,
        installment_amount=financing.current_installment,
        due_day=financing.due_day,
        first_installment_date=financing.first_installment_date,
        term_months=financing.term_months,
        is_paid_off=financing.is_paid_off,
        property_is_active=property_is_active,
    )


def payment_source(payment: Payment) -> DueSource:
    if payment.recurring_expense_id is not None:
        return DueSource(SourceKind.RECURRING_EXPENSE, payment.recurring_expense_id)
    if payment.financing_id is None:
        raise ValueError(f"pagamento {payment.id} sem origem")  # impedido pelo CHECK do banco
    return DueSource(SourceKind.FINANCING, payment.financing_id)


def to_payment_record(payment: Payment) -> PaymentRecord:
    return PaymentRecord(payment_source(payment), payment.reference_due_date, payment.amount_paid)
