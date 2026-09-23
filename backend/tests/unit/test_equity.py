import random
from datetime import date
from decimal import Decimal

from hypothesis import given
from hypothesis import strategies as st

from app.models.enums import PropertyType
from app.services.equity import (
    BalanceRecord,
    FinancingDebtInput,
    PropertyInput,
    ValuationRecord,
    acquisition_total,
    current_market_value,
    financing_debt,
    portfolio_summary,
    property_equity,
)

D = Decimal


def _property(**overrides) -> PropertyInput:
    fields = {"property_id": 1, "property_type": PropertyType.APARTAMENTO}
    return PropertyInput(**(fields | overrides))


def _valuation(day: date, value: str, record_id: int = 0) -> ValuationRecord:
    return ValuationRecord(valuation_date=day, value=D(value), record_id=record_id)


def _financing(balance: str | None = None, **overrides) -> FinancingDebtInput:
    balances = () if balance is None else (BalanceRecord(date(2026, 1, 1), D(balance), 1),)
    fields = {"financed_amount": D("300000.00"), "balances": balances}
    return FinancingDebtInput(**(fields | overrides))


# --- seção 6 do ESCOPO ---


def test_partial_ownership_net_worth() -> None:
    # 50% de um imóvel de R$ 400.000,00 com saldo devedor de R$ 100.000,00.
    prop = _property(
        ownership_percentage=D("50"),
        valuations=[_valuation(date(2026, 1, 1), "400000.00")],
        financings=[_financing("100000.00")],
    )

    equity = property_equity(prop)

    assert equity.market_value == D("400000.00")
    assert equity.gross == D("200000.00")
    assert equity.debt == D("100000.00")
    assert equity.net == D("100000.00")


def test_property_without_valuation_shows_no_value_and_does_not_break_totals() -> None:
    without_value = _property(property_id=1, financings=[_financing("50000.00")])
    with_value = _property(property_id=2, valuations=[_valuation(date(2026, 1, 1), "100000.00")])

    equity = property_equity(without_value)
    summary = portfolio_summary([without_value, with_value])

    assert equity.market_value is None
    assert equity.gross is None
    assert equity.net is None
    assert equity.debt == D("50000.00")
    assert summary.gross_total == D("100000.00")
    assert summary.debt_total == D("50000.00")
    assert summary.net_total == D("50000.00")
    assert summary.properties_without_value == 1


def test_property_without_financing_has_zero_debt() -> None:
    equity = property_equity(_property(valuations=[_valuation(date(2026, 1, 1), "300000.00")]))

    assert equity.debt == D("0.00")
    assert equity.net == D("300000.00")
    assert equity.debt_estimated is False


def test_property_with_two_financings_sums_both_debts() -> None:
    prop = _property(
        valuations=[_valuation(date(2026, 1, 1), "500000.00")],
        financings=[_financing("200000.00"), _financing("35000.50")],
    )

    equity = property_equity(prop)

    assert equity.debt == D("235000.50")
    assert equity.net == D("264999.50")


def test_paid_off_financing_is_not_debt() -> None:
    paid_off = _financing("80000.00", is_paid_off=True)
    prop = _property(
        valuations=[_valuation(date(2026, 1, 1), "300000.00")],
        financings=[paid_off, _financing("10000.00")],
    )

    assert financing_debt(paid_off).amount == D("0.00")
    assert property_equity(prop).debt == D("10000.00")


def test_inactive_property_is_out_of_totals() -> None:
    sold = _property(
        property_id=1,
        property_type=PropertyType.CASA,
        is_active=False,
        valuations=[_valuation(date(2026, 1, 1), "900000.00")],
        financings=[_financing("100.00")],
    )
    kept = _property(property_id=2, valuations=[_valuation(date(2026, 1, 1), "100000.00")])

    summary = portfolio_summary([sold, kept])

    assert summary.gross_total == D("100000.00")
    assert summary.debt_total == D("0.00")
    assert summary.property_count == 1
    assert summary.count_by_type == {PropertyType.APARTAMENTO: 1}


def test_current_value_is_most_recent_date_not_last_registered() -> None:
    valuations = [
        _valuation(date(2026, 6, 1), "450000.00", record_id=1),
        # cadastrada depois, mas com data mais antiga
        _valuation(date(2025, 1, 1), "380000.00", record_id=2),
    ]

    assert current_market_value(valuations) == D("450000.00")


# --- regras de dívida (decisões da Etapa 4) ---


def test_debt_is_most_recent_balance() -> None:
    financing = FinancingDebtInput(
        financed_amount=D("300000.00"),
        balances=[
            BalanceRecord(date(2026, 3, 1), D("250000.00"), record_id=2),
            BalanceRecord(date(2026, 1, 1), D("260000.00"), record_id=3),
        ],
    )

    assert financing_debt(financing).amount == D("250000.00")
    assert financing_debt(financing).estimated is False


def test_financing_without_balance_uses_financed_amount_as_estimate() -> None:
    financing = FinancingDebtInput(financed_amount=D("300000.00"))
    prop = _property(financings=[financing])

    assert financing_debt(financing).amount == D("300000.00")
    assert financing_debt(financing).estimated is True
    assert property_equity(prop).debt_estimated is True
    assert portfolio_summary([prop]).debt_estimated is True


# --- casos de borda da seção 5 do STACK ---


def test_empty_portfolio() -> None:
    summary = portfolio_summary([])

    assert summary.gross_total == D("0.00")
    assert summary.debt_total == D("0.00")
    assert summary.net_total == D("0.00")
    assert summary.property_count == 0
    assert summary.count_by_type == {}
    assert summary.debt_estimated is False


def test_zero_ownership_gives_zero_gross() -> None:
    prop = _property(ownership_percentage=D("0"), valuations=[_valuation(date(2026, 1, 1), "1.00")])

    assert property_equity(prop).gross == D("0.00")


def test_debt_greater_than_value_gives_negative_net() -> None:
    prop = _property(
        valuations=[_valuation(date(2026, 1, 1), "100000.00")],
        financings=[_financing("150000.00")],
    )

    assert property_equity(prop).net == D("-50000.00")
    assert portfolio_summary([prop]).net_total == D("-50000.00")


def test_valuations_on_same_date_use_last_registered() -> None:
    same_day = date(2026, 2, 28)
    valuations = [_valuation(same_day, "300000.00", 7), _valuation(same_day, "310000.00", 9)]

    assert current_market_value(valuations) == D("310000.00")


def test_balances_on_same_date_use_last_registered() -> None:
    same_day = date(2028, 2, 29)
    financing = FinancingDebtInput(
        financed_amount=D("1.00"),
        balances=[BalanceRecord(same_day, D("90.00"), 5), BalanceRecord(same_day, D("80.00"), 4)],
    )

    assert financing_debt(financing).amount == D("90.00")


def test_one_third_ownership_rounds_to_cents() -> None:
    prop = _property(
        ownership_percentage=D("33.3333"), valuations=[_valuation(date(2026, 1, 1), "100.00")]
    )

    # 100,00 × 33,3333% = 33,3333 -> 33,33 (arredondado só no fim)
    assert property_equity(prop).gross == D("33.33")


def test_rounding_half_up_on_gross() -> None:
    prop = _property(
        ownership_percentage=D("50"), valuations=[_valuation(date(2026, 1, 1), "0.01")]
    )

    # 0,01 × 50% = 0,005 -> 0,01
    assert property_equity(prop).gross == D("0.01")


def test_balance_or_valuation_in_middle_of_period() -> None:
    # Equivalente a "aportes e retiradas no meio do período": vale o registro mais recente.
    prop = _property(
        valuations=[
            _valuation(date(2026, 1, 1), "400000.00", 1),
            _valuation(date(2026, 1, 15), "420000.00", 2),
        ],
        financings=[
            FinancingDebtInput(
                financed_amount=D("300000.00"),
                balances=[
                    BalanceRecord(date(2026, 1, 1), D("200000.00"), 1),
                    BalanceRecord(date(2026, 1, 20), D("198000.00"), 2),
                ],
            )
        ],
    )

    assert property_equity(prop).net == D("222000.00")


def test_acquisition_total() -> None:
    assert acquisition_total(D("350000.00"), D("7000.00"), D("3500.33")) == D("360500.33")


# --- propriedades (Hypothesis) ---

money = st.decimals(min_value=0, max_value=10**9, places=2, allow_nan=False, allow_infinity=False)
percent = st.decimals(min_value=0, max_value=100, places=4, allow_nan=False, allow_infinity=False)
dates = st.dates(min_value=date(2000, 1, 1), max_value=date(2040, 12, 31))


def valuation_lists(min_size: int = 0, max_size: int = 4):
    # ids únicos, como no banco
    return st.lists(
        st.builds(ValuationRecord, dates, money, st.integers(0, 10**6)),
        min_size=min_size,
        max_size=max_size,
        unique_by=lambda v: v.record_id,
    )


@st.composite
def property_inputs(draw, property_id: int) -> PropertyInput:
    valuations = draw(valuation_lists(max_size=4))
    financings = draw(
        st.lists(
            st.builds(
                FinancingDebtInput,
                money,
                st.booleans(),
                st.lists(
                    st.builds(BalanceRecord, dates, money, st.integers(0, 10**6)),
                    max_size=3,
                    unique_by=lambda b: b.record_id,
                ),
            ),
            max_size=3,
        )
    )
    return PropertyInput(
        property_id=property_id,
        property_type=draw(st.sampled_from(list(PropertyType))),
        ownership_percentage=draw(percent),
        is_active=draw(st.booleans()),
        valuations=valuations,
        financings=financings,
    )


portfolios = st.integers(0, 6).flatmap(
    lambda n: st.tuples(*(property_inputs(i) for i in range(n))).map(list)
)


@given(portfolios)
def test_totals_match_the_listed_properties(properties: list[PropertyInput]) -> None:
    summary = portfolio_summary(properties)
    equities = [property_equity(p) for p in properties if p.is_active]

    assert summary.gross_total == sum((e.gross for e in equities if e.gross is not None), D(0))
    assert summary.debt_total == sum((e.debt for e in equities), D(0))
    assert summary.net_total == summary.gross_total - summary.debt_total
    assert sum(summary.count_by_type.values()) == summary.property_count


@given(portfolios)
def test_gross_values_have_exactly_two_places(properties: list[PropertyInput]) -> None:
    for prop in properties:
        gross = property_equity(prop).gross
        assert gross is None or gross.as_tuple().exponent == -2


@given(valuation_lists(min_size=1, max_size=20))
def test_current_value_does_not_depend_on_order(valuations: list[ValuationRecord]) -> None:
    shuffled = valuations[:]
    random.Random(0).shuffle(shuffled)

    assert current_market_value(shuffled) == current_market_value(valuations)
