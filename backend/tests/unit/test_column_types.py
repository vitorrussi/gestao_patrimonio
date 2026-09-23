from decimal import Decimal

import pytest
from sqlalchemy import Column, Integer, MetaData, Table, create_engine, insert, select, text
from sqlalchemy.exc import StatementError

from app.models.types import MoneyCents, ScaledDecimal

metadata = MetaData()
sample = Table(
    "sample",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("amount", MoneyCents()),
    Column("rate", ScaledDecimal(4)),
)


@pytest.fixture()
def engine():
    engine = create_engine("sqlite://")
    metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_values_are_stored_as_integers_and_read_as_decimal(engine) -> None:
    with engine.begin() as conn:
        conn.execute(insert(sample).values(amount=Decimal("1234.56"), rate=Decimal("9.5")))
        raw = conn.execute(text("SELECT amount, rate, typeof(amount), typeof(rate) FROM sample"))
        assert raw.one() == (123456, 95000, "integer", "integer")
        row = conn.execute(select(sample.c.amount, sample.c.rate)).one()

    assert row.amount == Decimal("1234.56")
    assert row.rate == Decimal("9.5")
    assert isinstance(row.amount, Decimal)
    assert isinstance(row.rate, Decimal)


def test_null_round_trips(engine) -> None:
    with engine.begin() as conn:
        conn.execute(insert(sample).values(amount=None, rate=None))
        row = conn.execute(select(sample.c.amount, sample.c.rate)).one()

    assert row.amount is None
    assert row.rate is None


def test_float_is_rejected(engine) -> None:
    with engine.begin() as conn, pytest.raises(StatementError):
        conn.execute(insert(sample).values(amount=0.1))


def test_extra_decimal_places_are_rejected(engine) -> None:
    with engine.begin() as conn, pytest.raises(StatementError):
        conn.execute(insert(sample).values(amount=Decimal("0.001")))
