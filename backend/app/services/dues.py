"""Vencimentos calculados na hora (não gravados no banco), status e totais do mês.

Funções puras: recebem regras e pagamentos em dataclasses e devolvem listas.
"""

from __future__ import annotations

import calendar
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, replace
from datetime import date
from decimal import Decimal
from enum import StrEnum

from app.models.enums import DueStatus, Frequency

ZERO = Decimal("0.00")

MONTHS_BETWEEN = {
    Frequency.MENSAL: 1,
    Frequency.BIMESTRAL: 2,
    Frequency.TRIMESTRAL: 3,
    Frequency.SEMESTRAL: 6,
    Frequency.ANUAL: 12,
}


class SourceKind(StrEnum):
    RECURRING_EXPENSE = "recurring_expense"
    FINANCING = "financing"


@dataclass(frozen=True, order=True)
class DueSource:
    kind: SourceKind
    source_id: int


@dataclass(frozen=True)
class ExpenseRule:
    expense_id: int
    property_id: int
    amount: Decimal
    frequency: Frequency
    due_day: int
    start_date: date
    end_date: date | None = None
    installment_count: int | None = None
    is_active: bool = True
    property_is_active: bool = True


@dataclass(frozen=True)
class FinancingRule:
    financing_id: int
    property_id: int
    installment_amount: Decimal
    due_day: int
    first_installment_date: date
    term_months: int
    is_paid_off: bool = False
    property_is_active: bool = True


@dataclass(frozen=True)
class Due:
    source: DueSource
    property_id: int
    due_date: date
    expected_amount: Decimal


@dataclass(frozen=True)
class PaymentRecord:
    source: DueSource
    reference_due_date: date
    amount_paid: Decimal


@dataclass(frozen=True)
class DueWithStatus:
    due: Due
    status: DueStatus
    amount_paid: Decimal | None


@dataclass(frozen=True)
class MonthSummary:
    items: tuple[DueWithStatus, ...]
    total_expected: Decimal
    total_paid: Decimal  # soma do que foi efetivamente pago (pode ter juros/multa)
    total_open: Decimal  # previsto dos vencimentos ainda não pagos (a pagar + atrasados)
    total_overdue: Decimal  # parte de total_open que já está atrasada


# --- datas ---


def add_months(day: date, months: int) -> tuple[int, int]:
    """(ano, mês) de `day` deslocado em `months` meses."""
    index = day.year * 12 + (day.month - 1) + months
    return index // 12, index % 12 + 1


def due_date_in_month(year: int, month: int, due_day: int) -> date:
    """Dia de vencimento no mês, limitado ao último dia (31 -> 30/abr, 28 ou 29/fev)."""
    return date(year, month, min(due_day, calendar.monthrange(year, month)[1]))


def month_period(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


# --- geração ---


def _first_due_month(start_date: date, due_day: int) -> date:
    """1º dia do mês do primeiro vencimento na data de início ou depois dela."""
    if due_date_in_month(start_date.year, start_date.month, due_day) >= start_date:
        return start_date.replace(day=1)
    year, month = add_months(start_date, 1)
    return date(year, month, 1)


def _expense_occurrences(rule: ExpenseRule) -> Iterator[date]:
    """Datas de vencimento da despesa em ordem, respeitando nº de parcelas e data de fim."""
    first_month = _first_due_month(rule.start_date, rule.due_day)
    step = MONTHS_BETWEEN.get(rule.frequency, 0)
    limit = 1 if rule.frequency is Frequency.UNICA else rule.installment_count
    index = 0
    while limit is None or index < limit:
        due = due_date_in_month(*add_months(first_month, index * step), rule.due_day)
        if rule.end_date is not None and due > rule.end_date:
            return
        yield due
        index += 1


def expense_dues(rule: ExpenseRule, start: date, end: date) -> list[Due]:
    if not (rule.is_active and rule.property_is_active):
        return []
    source = DueSource(SourceKind.RECURRING_EXPENSE, rule.expense_id)
    dues = []
    for due_date in _expense_occurrences(rule):
        if due_date > end:
            break
        if due_date >= start:
            dues.append(Due(source, rule.property_id, due_date, rule.amount))
    return dues


def financing_dues(rule: FinancingRule, start: date, end: date) -> list[Due]:
    """Parcelas mensais a partir do mês da 1ª parcela, no dia de vencimento, até o prazo."""
    if rule.is_paid_off or not rule.property_is_active:
        return []
    source = DueSource(SourceKind.FINANCING, rule.financing_id)
    dues = []
    for index in range(rule.term_months):
        due_date = due_date_in_month(*add_months(rule.first_installment_date, index), rule.due_day)
        if due_date > end:
            break
        if due_date >= start:
            dues.append(Due(source, rule.property_id, due_date, rule.installment_amount))
    return dues


def expense_has_due_on(rule: ExpenseRule, day: date) -> bool:
    """`day` é vencimento da despesa? Ignora ativo/inativo: vencimento antigo segue pagável."""
    rule = replace(rule, is_active=True, property_is_active=True)
    return bool(expense_dues(rule, day, day))


def financing_has_due_on(rule: FinancingRule, day: date) -> bool:
    """`day` é uma parcela do financiamento? Ignora quitado/inativo pelo mesmo motivo."""
    rule = replace(rule, is_paid_off=False, property_is_active=True)
    return bool(financing_dues(rule, day, day))


def dues_in_period(
    expenses: Iterable[ExpenseRule], financings: Iterable[FinancingRule], start: date, end: date
) -> list[Due]:
    """Todos os vencimentos em [start, end], ordenados por data e origem."""
    dues = [due for rule in expenses for due in expense_dues(rule, start, end)]
    dues += [due for rule in financings for due in financing_dues(rule, start, end)]
    return sorted(dues, key=lambda due: (due.due_date, due.source))


# --- status e totais ---


def _status(due: Due, paid: bool, today: date) -> DueStatus:
    if paid:
        return DueStatus.PAGO
    # Atrasado só no dia seguinte ao vencimento, não no próprio dia.
    if due.due_date < today:
        return DueStatus.ATRASADO
    return DueStatus.A_PAGAR


def with_status(
    dues: Iterable[Due], payments: Iterable[PaymentRecord], today: date
) -> list[DueWithStatus]:
    """Pago quando existe pagamento com a mesma origem e data de referência (qualquer valor)."""
    paid = {(p.source, p.reference_due_date): p.amount_paid for p in payments}
    items = []
    for due in dues:
        amount_paid = paid.get((due.source, due.due_date))
        status = _status(due, amount_paid is not None, today)
        items.append(DueWithStatus(due, status, amount_paid))
    return items


def summarize(items: Iterable[DueWithStatus]) -> MonthSummary:
    items = tuple(items)
    unpaid = [i for i in items if i.status is not DueStatus.PAGO]
    return MonthSummary(
        items=items,
        total_expected=sum((i.due.expected_amount for i in items), ZERO),
        total_paid=sum((i.amount_paid for i in items if i.amount_paid is not None), ZERO),
        total_open=sum((i.due.expected_amount for i in unpaid), ZERO),
        total_overdue=sum(
            (i.due.expected_amount for i in unpaid if i.status is DueStatus.ATRASADO), ZERO
        ),
    )


def month_commitments(
    expenses: Iterable[ExpenseRule],
    financings: Iterable[FinancingRule],
    payments: Iterable[PaymentRecord],
    year: int,
    month: int,
    today: date,
) -> MonthSummary:
    """Compromissos do mês: tudo que vence no mês, com status e totais."""
    start, end = month_period(year, month)
    dues = dues_in_period(expenses, financings, start, end)
    return summarize(with_status(dues, payments, today))
