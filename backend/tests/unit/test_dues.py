from datetime import date, timedelta
from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.models.enums import DueStatus, Frequency
from app.services.dues import (
    MONTHS_BETWEEN,
    Due,
    DueSource,
    ExpenseRule,
    FinancingRule,
    PaymentRecord,
    SourceKind,
    add_months,
    due_date_in_month,
    dues_in_period,
    expense_dues,
    financing_dues,
    month_commitments,
    month_period,
    summarize,
    with_status,
)

D = Decimal
FOREVER = (date(2000, 1, 1), date(2100, 12, 31))


def _expense(**overrides) -> ExpenseRule:
    fields = {
        "expense_id": 1,
        "property_id": 1,
        "amount": D("650.00"),
        "frequency": Frequency.MENSAL,
        "due_day": 10,
        "start_date": date(2026, 1, 1),
    }
    return ExpenseRule(**(fields | overrides))


def _financing(**overrides) -> FinancingRule:
    fields = {
        "financing_id": 1,
        "property_id": 1,
        "installment_amount": D("2500.00"),
        "due_day": 15,
        "first_installment_date": date(2026, 1, 15),
        "term_months": 360,
    }
    return FinancingRule(**(fields | overrides))


def _dates(dues: list[Due]) -> list[date]:
    return [due.due_date for due in dues]


def _payment(source: DueSource, day: date, amount: str = "650.00") -> PaymentRecord:
    return PaymentRecord(source=source, reference_due_date=day, amount_paid=D(amount))


EXPENSE_1 = DueSource(SourceKind.RECURRING_EXPENSE, 1)


# --- seção 6 do ESCOPO ---


def test_due_day_31_in_30_day_months_and_february() -> None:
    rule = _expense(due_day=31, start_date=date(2027, 1, 1))

    dues = expense_dues(rule, date(2027, 1, 1), date(2027, 5, 31))

    assert _dates(dues) == [
        date(2027, 1, 31),
        date(2027, 2, 28),
        date(2027, 3, 31),  # volta a 31: o limite de um mês não se acumula
        date(2027, 4, 30),
        date(2027, 5, 31),
    ]


def test_due_day_31_in_february_of_leap_year() -> None:
    rule = _expense(due_day=31, start_date=date(2028, 2, 1))

    assert _dates(expense_dues(rule, date(2028, 2, 1), date(2028, 2, 29))) == [date(2028, 2, 29)]


def test_iptu_in_10_installments_generates_exactly_10_dues() -> None:
    rule = _expense(frequency=Frequency.MENSAL, installment_count=10, start_date=date(2026, 2, 1))

    dues = expense_dues(rule, *FOREVER)

    assert len(dues) == 10
    assert dues[0].due_date == date(2026, 2, 10)
    assert dues[-1].due_date == date(2026, 11, 10)


@pytest.mark.parametrize(
    ("frequency", "expected"),
    [
        (Frequency.ANUAL, [date(2026, 3, 10), date(2027, 3, 10), date(2028, 3, 10)]),
        (Frequency.SEMESTRAL, [date(2026, 3, 10), date(2026, 9, 10), date(2027, 3, 10)]),
        (Frequency.TRIMESTRAL, [date(2026, 3, 10), date(2026, 6, 10), date(2026, 9, 10)]),
        (Frequency.BIMESTRAL, [date(2026, 3, 10), date(2026, 5, 10), date(2026, 7, 10)]),
        (Frequency.UNICA, [date(2026, 3, 10)]),
    ],
)
def test_frequencies_generate_correct_dates(frequency: Frequency, expected: list[date]) -> None:
    rule = _expense(frequency=frequency, start_date=date(2026, 3, 1))

    assert _dates(expense_dues(rule, *FOREVER))[:3] == expected


def test_single_expense_ignores_installment_count() -> None:
    rule = _expense(frequency=Frequency.UNICA, installment_count=5)

    assert len(expense_dues(rule, *FOREVER)) == 1


def test_due_becomes_overdue_the_day_after_not_on_the_day() -> None:
    due_day = date(2026, 3, 10)
    dues = expense_dues(_expense(), due_day, due_day)

    assert with_status(dues, [], today=date(2026, 3, 9))[0].status is DueStatus.A_PAGAR
    assert with_status(dues, [], today=due_day)[0].status is DueStatus.A_PAGAR
    assert with_status(dues, [], today=date(2026, 3, 11))[0].status is DueStatus.ATRASADO


def test_payment_with_different_amount_settles_the_due() -> None:
    dues = expense_dues(_expense(), date(2026, 3, 1), date(2026, 3, 31))

    [item] = with_status(dues, [_payment(EXPENSE_1, date(2026, 3, 10), "672.40")], date(2026, 4, 1))

    assert item.status is DueStatus.PAGO
    assert item.amount_paid == D("672.40")
    assert item.due.expected_amount == D("650.00")


def test_due_is_paid_only_with_same_source_and_reference_date() -> None:
    dues = expense_dues(_expense(), date(2026, 3, 1), date(2026, 3, 31))
    wrong_date = _payment(EXPENSE_1, date(2026, 3, 11))
    wrong_source = _payment(DueSource(SourceKind.FINANCING, 1), date(2026, 3, 10))
    other_expense = _payment(DueSource(SourceKind.RECURRING_EXPENSE, 2), date(2026, 3, 10))

    [item] = with_status(dues, [wrong_date, wrong_source, other_expense], date(2026, 3, 1))

    assert item.status is DueStatus.A_PAGAR
    assert item.amount_paid is None


def test_month_totals_neither_lose_nor_gain_cents() -> None:
    rules = [
        _expense(expense_id=i, amount=D("33.33"), start_date=date(2026, 5, 1)) for i in (1, 2, 3)
    ]

    summary = month_commitments(rules, [], [], 2026, 5, today=date(2026, 5, 1))

    assert summary.total_expected == D("99.99")
    assert summary.total_open == D("99.99")
    assert summary.total_paid == D("0.00")


def test_ended_expense_generates_nothing_after_end_but_keeps_old_payments() -> None:
    rule = _expense(end_date=date(2026, 3, 31))
    payments = [_payment(EXPENSE_1, date(2026, 1, 10)), _payment(EXPENSE_1, date(2026, 2, 10))]

    items = with_status(
        expense_dues(rule, date(2026, 1, 1), date(2026, 6, 30)), payments, date(2026, 7, 1)
    )

    assert [i.due.due_date for i in items] == [
        date(2026, 1, 10),
        date(2026, 2, 10),
        date(2026, 3, 10),
    ]
    assert [i.status for i in items] == [DueStatus.PAGO, DueStatus.PAGO, DueStatus.ATRASADO]


def test_end_date_on_due_day_includes_that_due() -> None:
    rule = _expense(end_date=date(2026, 3, 10))

    assert _dates(expense_dues(rule, *FOREVER))[-1] == date(2026, 3, 10)


def test_period_returns_only_dues_inside_it() -> None:
    dues = dues_in_period([_expense()], [_financing()], date(2026, 4, 1), date(2026, 4, 30))

    assert _dates(dues) == [date(2026, 4, 10), date(2026, 4, 15)]


def test_paid_off_financing_is_not_in_month_commitments() -> None:
    summary = month_commitments(
        [], [_financing(is_paid_off=True)], [], 2026, 4, today=date(2026, 4, 1)
    )

    assert summary.items == ()
    assert summary.total_expected == D("0.00")


def test_inactive_property_is_not_in_month_commitments() -> None:
    summary = month_commitments(
        [_expense(property_is_active=False)],
        [_financing(property_is_active=False)],
        [],
        2026,
        4,
        today=date(2026, 4, 1),
    )

    assert summary.items == ()


def test_inactive_expense_generates_nothing() -> None:
    assert expense_dues(_expense(is_active=False), *FOREVER) == []


# --- regras de geração (decisões da Etapa 4) ---


def test_first_due_is_next_month_when_start_is_after_due_day() -> None:
    rule = _expense(due_day=10, start_date=date(2026, 1, 15))

    assert _dates(expense_dues(rule, *FOREVER))[0] == date(2026, 2, 10)


def test_first_due_is_same_day_when_start_is_the_due_day() -> None:
    rule = _expense(due_day=10, start_date=date(2026, 1, 10))

    assert _dates(expense_dues(rule, *FOREVER))[0] == date(2026, 1, 10)


def test_financing_generates_term_installments_from_first_month() -> None:
    rule = _financing(term_months=3, due_day=31, first_installment_date=date(2027, 1, 31))

    dues = financing_dues(rule, *FOREVER)

    assert _dates(dues) == [date(2027, 1, 31), date(2027, 2, 28), date(2027, 3, 31)]
    assert all(due.expected_amount == D("2500.00") for due in dues)
    assert all(due.source == DueSource(SourceKind.FINANCING, 1) for due in dues)


def test_due_day_29_in_leap_and_common_years() -> None:
    rule = _expense(due_day=29, frequency=Frequency.ANUAL, start_date=date(2027, 2, 1))

    assert _dates(expense_dues(rule, *FOREVER))[:3] == [
        date(2027, 2, 28),
        date(2028, 2, 29),
        date(2029, 2, 28),
    ]


def test_dues_are_sorted_by_date_then_source() -> None:
    same_day_expense = _expense(due_day=15)
    dues = dues_in_period([same_day_expense], [_financing()], date(2026, 1, 1), date(2026, 1, 31))

    assert [d.source.kind for d in dues] == [SourceKind.FINANCING, SourceKind.RECURRING_EXPENSE]


def test_status_mix_and_totals() -> None:
    rules = [
        _expense(expense_id=1, amount=D("100.00"), due_day=5),
        _expense(expense_id=2, amount=D("200.00"), due_day=10),
        _expense(expense_id=3, amount=D("300.00"), due_day=20),
    ]
    payments = [_payment(EXPENSE_1, date(2026, 6, 5), "105.50")]

    summary = month_commitments(rules, [], payments, 2026, 6, today=date(2026, 6, 15))

    assert [i.status for i in summary.items] == [
        DueStatus.PAGO,
        DueStatus.ATRASADO,
        DueStatus.A_PAGAR,
    ]
    assert summary.total_expected == D("600.00")
    assert summary.total_paid == D("105.50")
    assert summary.total_open == D("500.00")
    assert summary.total_overdue == D("200.00")


def test_month_period_handles_february() -> None:
    assert month_period(2028, 2) == (date(2028, 2, 1), date(2028, 2, 29))
    assert month_period(2027, 2) == (date(2027, 2, 1), date(2027, 2, 28))


def test_add_months_crosses_year() -> None:
    assert add_months(date(2026, 11, 30), 3) == (2027, 2)
    assert add_months(date(2026, 1, 1), -1) == (2025, 12)


# --- propriedades (Hypothesis) ---

frequencies = st.sampled_from([f for f in Frequency if f is not Frequency.UNICA])
start_dates = st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))
due_days = st.integers(min_value=1, max_value=31)
money = st.decimals(min_value=0, max_value=10**7, places=2, allow_nan=False, allow_infinity=False)


@given(frequencies, due_days, start_dates, st.integers(min_value=1, max_value=60))
def test_installments_generate_exactly_n_increasing_dues(
    frequency: Frequency, due_day: int, start: date, installments: int
) -> None:
    rule = _expense(
        frequency=frequency, due_day=due_day, start_date=start, installment_count=installments
    )

    dues = _dates(expense_dues(rule, *FOREVER))

    assert len(dues) == installments
    assert dues[0] >= start
    assert all(a < b for a, b in zip(dues, dues[1:], strict=False))
    for day in dues:
        assert day == due_date_in_month(day.year, day.month, due_day)
    step = MONTHS_BETWEEN[frequency]
    for a, b in zip(dues, dues[1:], strict=False):
        assert (b.year * 12 + b.month) - (a.year * 12 + a.month) == step


@given(frequencies, due_days, start_dates, st.integers(min_value=2020, max_value=2031))
def test_months_of_a_year_add_up_to_the_whole_year(
    frequency: Frequency, due_day: int, start: date, year: int
) -> None:
    rule = _expense(frequency=frequency, due_day=due_day, start_date=start)

    by_month = [due for m in range(1, 13) for due in expense_dues(rule, *month_period(year, m))]

    assert by_month == expense_dues(rule, date(year, 1, 1), date(year, 12, 31))


@given(
    st.lists(st.tuples(money, st.booleans(), st.integers(0, 60), money), max_size=30),
    st.dates(min_value=date(2026, 1, 1), max_value=date(2026, 3, 1)),
)
def test_summary_totals_are_exact_sums(
    rows: list[tuple[Decimal, bool, int, Decimal]], today: date
) -> None:
    dues = [
        Due(
            DueSource(SourceKind.RECURRING_EXPENSE, i),
            1,
            date(2026, 1, 1) + timedelta(days),
            amount,
        )
        for i, (amount, _, days, _) in enumerate(rows)
    ]
    payments = [
        PaymentRecord(due.source, due.due_date, paid)
        for due, (_, is_paid, _, paid) in zip(dues, rows, strict=True)
        if is_paid
    ]

    summary = summarize(with_status(dues, payments, today))
    paid_items = [i for i in summary.items if i.status is DueStatus.PAGO]

    assert summary.total_expected == sum((d.expected_amount for d in dues), D(0))
    assert summary.total_open + sum((i.due.expected_amount for i in paid_items), D(0)) == (
        summary.total_expected
    )
    assert summary.total_paid == sum((p.amount_paid for p in payments), D(0))
    assert summary.total_overdue <= summary.total_open
