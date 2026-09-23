from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from app.services.money import (
    InexactDecimalError,
    from_cents,
    from_scaled_int,
    round_to_cents,
    to_cents,
    to_scaled_int,
)


@pytest.mark.parametrize(
    ("value", "cents"),
    [
        ("0.01", 1),
        ("0.10", 10),
        ("0.1", 10),
        ("33.33", 3333),
        ("400000.00", 40_000_000),
        ("0", 0),
        ("-0.01", -1),
        ("-150.5", -15050),
    ],
)
def test_to_cents_is_exact(value: str, cents: int) -> None:
    assert to_cents(Decimal(value)) == cents


def test_from_cents_keeps_two_places() -> None:
    assert str(from_cents(1)) == "0.01"
    assert str(from_cents(10)) == "0.10"
    assert str(from_cents(0)) == "0.00"
    assert str(from_cents(-15050)) == "-150.50"


def test_33_33_times_three_neither_loses_nor_gains_cents() -> None:
    parts = [Decimal("33.33")] * 3

    assert sum(to_cents(part) for part in parts) == 9999
    assert from_cents(sum(to_cents(part) for part in parts)) == Decimal("99.99")


def test_to_cents_refuses_to_round_silently() -> None:
    with pytest.raises(InexactDecimalError):
        to_cents(Decimal("0.001"))


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")])
def test_to_cents_rejects_non_finite(value: Decimal) -> None:
    with pytest.raises(InexactDecimalError):
        to_cents(value)


@pytest.mark.parametrize("value", [0.1, 1, "0.10"])
def test_to_cents_rejects_non_decimal(value: object) -> None:
    with pytest.raises(TypeError):
        to_cents(value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [1.0, "1", True, None])
def test_from_cents_rejects_non_int(value: object) -> None:
    with pytest.raises(TypeError):
        from_cents(value)  # type: ignore[arg-type]


def test_scaled_int_with_four_places() -> None:
    assert to_scaled_int(Decimal("33.3333"), 4) == 333333
    assert from_scaled_int(1_000_000, 4) == Decimal("100")
    with pytest.raises(InexactDecimalError):
        to_scaled_int(Decimal("33.33333"), 4)


@pytest.mark.parametrize(
    ("value", "rounded"),
    [
        ("0.004", "0.00"),
        ("0.005", "0.01"),
        ("33.333333", "33.33"),
        ("-0.005", "-0.01"),
        ("2.675", "2.68"),
    ],
)
def test_round_to_cents_half_up(value: str, rounded: str) -> None:
    assert round_to_cents(Decimal(value)) == Decimal(rounded)


@given(st.integers(min_value=-(10**15), max_value=10**15))
def test_cents_round_trip(cents: int) -> None:
    assert to_cents(from_cents(cents)) == cents


@given(st.decimals(min_value=-(10**12), max_value=10**12, places=2, allow_nan=False))
def test_decimal_round_trip(value: Decimal) -> None:
    assert from_cents(to_cents(value)) == value


@given(st.lists(st.integers(min_value=0, max_value=10**12), max_size=50))
def test_sum_in_cents_matches_sum_in_decimal(cents_list: list[int]) -> None:
    assert from_cents(sum(cents_list)) == sum((from_cents(c) for c in cents_list), Decimal(0))
