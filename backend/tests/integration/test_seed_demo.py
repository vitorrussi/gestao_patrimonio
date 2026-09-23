"""O seed de demonstração roda no schema migrado e produz uma carteira "cheia"."""

from collections.abc import Iterator
from datetime import date
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.db import create_engine_with_pragmas, make_session_factory
from app.models.enums import DueStatus
from app.repositories.portfolio import load_portfolio
from app.services.dues import month_commitments
from app.services.equity import portfolio_summary
from app.services.money import from_cents
from scripts import seed_demo
from tests.migrations_helpers import upgrade_to_head

TODAY = date(2026, 9, 23)


@pytest.fixture()
def demo_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Session]:
    url = upgrade_to_head(tmp_path / "demo", monkeypatch)
    engine = create_engine_with_pragmas(url)
    with make_session_factory(engine)() as session:
        yield session
    engine.dispose()


def test_seed_fills_portfolio_and_commitments(demo_session: Session) -> None:
    user = seed_demo.seed(demo_session, TODAY)
    portfolio = load_portfolio(demo_session, user.id)

    summary = portfolio_summary(portfolio.property_inputs)
    assert len(portfolio.properties) == 6
    assert summary.property_count == 5  # a casa vendida fica fora
    assert summary.properties_without_value == 1  # o terreno
    assert summary.debt_estimated is True  # financiamento sem saldo lançado
    assert summary.gross_total > from_cents(0)

    month = month_commitments(
        portfolio.expense_rules,
        portfolio.financing_rules,
        portfolio.payments,
        TODAY.year,
        TODAY.month,
        TODAY,
    )
    statuses = {item.status for item in month.items}
    assert statuses == {DueStatus.PAGO, DueStatus.ATRASADO, DueStatus.A_PAGAR}
    assert len(portfolio.payments) > 20


def test_seed_payments_are_real_dues_and_never_in_the_future(demo_session: Session) -> None:
    user = seed_demo.seed(demo_session, TODAY)
    portfolio = load_portfolio(demo_session, user.id)

    assert all(p.reference_due_date <= TODAY for p in portfolio.payments)
    paid_dates = {(p.source, p.reference_due_date) for p in portfolio.payments}
    assert len(paid_dates) == len(portfolio.payments)


def test_seed_refuses_database_that_is_not_demo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "real"))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(seed_demo.NotADemoDatabase):
        seed_demo.main()


def test_seed_main_runs_on_demo_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    upgrade_to_head(tmp_path / "demo", monkeypatch)

    seed_demo.main()

    assert seed_demo.DEMO_EMAIL in capsys.readouterr().out
