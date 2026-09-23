"""Carteira fictícia para demonstração: `python -m scripts.seed_demo` (a partir de backend/).

Só roda em banco cujo caminho contém "demo" — nunca no banco real. As datas são montadas em
torno de hoje, para sempre haver meses pagos, vencimentos atrasados e a pagar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app import clock
from app.config import Config
from app.db import create_engine_with_pragmas, make_session_factory
from app.models import (
    DebtBalance,
    Financing,
    MarketValuation,
    Payment,
    Property,
    RecurringExpense,
    User,
)
from app.models.enums import (
    AcquisitionMethod,
    AmortizationSystem,
    ExpenseType,
    Frequency,
    InterestIndex,
    PropertyType,
    PropertyUsage,
    ValuationSource,
)
from app.repositories.mappers import to_expense_rule, to_financing_rule
from app.services.auth import register_user
from app.services.dues import Due, SourceKind, dues_in_period
from app.services.money import round_to_cents

DEMO_EMAIL = "demo@example.com"
DEMO_PASSWORD = "demo-patrimonio"
PAYMENT_HISTORY_DAYS = 180

D = Decimal


class NotADemoDatabase(RuntimeError):
    pass


def _years_ago(today: date, years: int, month: int, day: int) -> date:
    return date(today.year - years, month, day)


@dataclass(frozen=True)
class Seeder:
    session: Session
    user: User
    today: date

    def add(self, obj: Any) -> Any:
        self.session.add(obj)
        self.session.flush()
        return obj

    def prop(self, **fields: Any) -> Property:
        return self.add(Property(user_id=self.user.id, **fields))

    def valuations(self, prop: Property, history: list[tuple[date, str, ValuationSource]]) -> None:
        for day, value, source in history:
            self.add(
                MarketValuation(
                    property_id=prop.id, valuation_date=day, value=D(value), source=source
                )
            )

    def expense(self, prop: Property, **fields: Any) -> RecurringExpense:
        return self.add(RecurringExpense(property_id=prop.id, **fields))

    def financing(self, prop: Property, balances: list[tuple[date, str]], **fields: Any) -> None:
        financing = self.add(Financing(property_id=prop.id, **fields))
        for day, balance in balances:
            self.add(DebtBalance(financing_id=financing.id, balance_date=day, balance=D(balance)))


def _apartment(s: Seeder) -> None:
    t = s.today
    apto = s.prop(
        nickname="Apto Centro",
        property_type=PropertyType.APARTAMENTO,
        usage=PropertyUsage.ALUGADO,
        street="Rua das Palmeiras",
        number="1200",
        complement="Apto 804",
        neighborhood="Centro",
        city="Joinville",
        state="SC",
        zip_code="89201-100",
        registration_number="45.871",
        registry_office="1º Registro de Imóveis de Joinville",
        municipal_registration="13.20.34.56.0789",
        acquisition_date=_years_ago(t, 6, 5, 20),
        acquisition_method=AcquisitionMethod.COMPRA,
        purchase_price=D("380000.00"),
        itbi=D("7600.00"),
        deed_registration=D("4230.55"),
    )
    s.valuations(
        apto,
        [
            (_years_ago(t, 6, 5, 20), "380000.00", ValuationSource.LAUDO),
            (_years_ago(t, 3, 8, 1), "430000.00", ValuationSource.CORRETOR),
            (_years_ago(t, 1, 3, 15), "468000.00", ValuationSource.ANUNCIO_SIMILAR),
        ],
    )
    s.financing(
        apto,
        [
            (_years_ago(t, 2, 12, 31), "268450.12"),
            (_years_ago(t, 1, 12, 31), "257310.77"),
            (t.replace(day=1) - timedelta(days=1), "251980.40"),
        ],
        lender="Caixa",
        contract_number="8.4444.0123456-7",
        financed_amount=D("304000.00"),
        amortization_system=AmortizationSystem.SAC,
        annual_interest_rate=D("8.9"),
        interest_index=InterestIndex.TR,
        term_months=360,
        first_installment_date=_years_ago(t, 6, 6, 10),
        due_day=10,
        current_installment=D("2187.34"),
    )
    s.expense(
        apto,
        expense_type=ExpenseType.CONDOMINIO,
        description="Condomínio",
        amount=D("720.00"),
        frequency=Frequency.MENSAL,
        due_day=5,
        start_date=_years_ago(t, 6, 6, 1),
    )
    s.expense(
        apto,
        expense_type=ExpenseType.IPTU,
        description=f"IPTU {t.year} — 10x",
        amount=D("185.40"),
        frequency=Frequency.MENSAL,
        due_day=15,
        start_date=date(t.year, 2, 1),
        installment_count=10,
    )
    s.expense(
        apto,
        expense_type=ExpenseType.SEGURO,
        description="Seguro residencial",
        amount=D("640.00"),
        frequency=Frequency.ANUAL,
        due_day=20,
        start_date=_years_ago(t, 2, (t.month % 12) + 1, 1),
    )


def _beach_house(s: Seeder) -> None:
    t = s.today
    casa = s.prop(
        nickname="Casa Jurerê",
        property_type=PropertyType.CASA_CONDOMINIO,
        usage=PropertyUsage.MORADIA_PROPRIA,
        street="Alameda das Gaivotas",
        number="77",
        neighborhood="Jurerê Internacional",
        city="Florianópolis",
        state="SC",
        zip_code="88053-300",
        registration_number="102.334",
        ownership_percentage=D("50"),
        acquisition_date=_years_ago(t, 9, 2, 3),
        acquisition_method=AcquisitionMethod.HERANCA,
    )
    s.valuations(
        casa,
        [
            (_years_ago(t, 4, 1, 10), "1050000.00", ValuationSource.ESTIMATIVA_PROPRIA),
            (_years_ago(t, 1, 11, 5), "1280000.00", ValuationSource.CORRETOR),
        ],
    )
    s.expense(
        casa,
        expense_type=ExpenseType.CONDOMINIO,
        description="Condomínio do loteamento",
        amount=D("1340.00"),
        frequency=Frequency.MENSAL,
        due_day=10,
        start_date=_years_ago(t, 5, 1, 1),
    )
    s.expense(
        casa,
        expense_type=ExpenseType.LUZ,
        description="Energia (média)",
        amount=D("310.00"),
        frequency=Frequency.MENSAL,
        due_day=22,
        start_date=_years_ago(t, 5, 1, 1),
    )


def _land(s: Seeder) -> None:
    t = s.today
    terreno = s.prop(
        nickname="Terreno Pirabeiraba",
        property_type=PropertyType.TERRENO,
        usage=PropertyUsage.VAZIO,
        city="Joinville",
        state="SC",
        acquisition_date=_years_ago(t, 3, 9, 12),
        acquisition_method=AcquisitionMethod.COMPRA,
        purchase_price=D("145000.00"),
        itbi=D("2900.00"),
        deed_registration=D("1870.00"),
    )
    s.expense(
        terreno,
        expense_type=ExpenseType.MANUTENCAO,
        description="Roçada",
        amount=D("250.00"),
        frequency=Frequency.BIMESTRAL,
        due_day=28,
        start_date=_years_ago(t, 1, 1, 1),
    )


def _office(s: Seeder) -> None:
    t = s.today
    sala = s.prop(
        nickname="Sala Comercial 1203",
        property_type=PropertyType.SALA_COMERCIAL,
        usage=PropertyUsage.COMERCIAL_PROPRIO,
        street="Av. Beira Rio",
        number="300",
        complement="Sala 1203",
        city="Joinville",
        state="SC",
        zip_code="89202-000",
        acquisition_date=_years_ago(t, 2, 4, 1),
        acquisition_method=AcquisitionMethod.COMPRA,
        purchase_price=D("290000.00"),
        itbi=D("5800.00"),
        deed_registration=D("3100.00"),
    )
    s.valuations(sala, [(_years_ago(t, 0, 1, 20), "315000.00", ValuationSource.LAUDO)])
    s.financing(
        sala,
        [],  # sem saldo lançado: a dívida aparece como estimativa
        lender="Construtora Horizonte",
        financed_amount=D("120000.00"),
        amortization_system=AmortizationSystem.PRICE,
        annual_interest_rate=D("12"),
        interest_index=InterestIndex.PREFIXADO,
        term_months=96,
        first_installment_date=_years_ago(t, 2, 5, 25),
        due_day=25,
        current_installment=D("1948.60"),
    )
    s.financing(
        sala,
        [(_years_ago(t, 1, 6, 30), "0.00")],
        lender="Banco do Brasil (entrada)",
        financed_amount=D("30000.00"),
        amortization_system=AmortizationSystem.SAC,
        annual_interest_rate=D("14.5"),
        interest_index=InterestIndex.PREFIXADO,
        term_months=12,
        first_installment_date=_years_ago(t, 2, 5, 25),
        due_day=25,
        current_installment=D("2650.00"),
        is_paid_off=True,
    )
    s.expense(
        sala,
        expense_type=ExpenseType.CONDOMINIO,
        description="Condomínio comercial",
        amount=D("890.00"),
        frequency=Frequency.MENSAL,
        due_day=8,
        start_date=_years_ago(t, 2, 5, 1),
    )


def _garage_and_sold(s: Seeder) -> None:
    t = s.today
    vaga = s.prop(
        nickname="Vaga Garagem 12",
        property_type=PropertyType.VAGA_GARAGEM,
        usage=PropertyUsage.ALUGADO,
        city="Joinville",
        state="SC",
        ownership_percentage=D("33.3333"),
        acquisition_method=AcquisitionMethod.HERANCA,
    )
    s.valuations(vaga, [(_years_ago(t, 1, 7, 1), "45000.00", ValuationSource.ESTIMATIVA_PROPRIA)])
    vendida = s.prop(
        nickname="Casa Antiga (vendida)",
        property_type=PropertyType.CASA,
        usage=PropertyUsage.VAZIO,
        city="Blumenau",
        state="SC",
        acquisition_date=_years_ago(t, 15, 3, 10),
        acquisition_method=AcquisitionMethod.CONSTRUCAO,
        purchase_price=D("210000.00"),
        is_active=False,
    )
    s.valuations(vendida, [(_years_ago(t, 1, 2, 1), "520000.00", ValuationSource.CORRETOR)])


def _payment_decision(due: Due, index: int, today: date) -> str:
    """'skip' deixa em aberto; 'late' paga com juros; 'ok' paga em dia (padrão fixo)."""
    this_month = (due.due_date.year, due.due_date.month) == (today.year, today.month)
    if this_month and index % 3 == 0:
        return "skip"
    if not this_month and index % 13 == 7:
        return "skip"
    return "late" if index % 5 == 0 else "ok"


def _payment_for(due: Due, decision: str, today: date) -> Payment:
    source = due.source
    is_expense = source.kind is SourceKind.RECURRING_EXPENSE
    late = decision == "late"
    return Payment(
        recurring_expense_id=source.source_id if is_expense else None,
        financing_id=None if is_expense else source.source_id,
        reference_due_date=due.due_date,
        payment_date=min(today, due.due_date + timedelta(days=4 if late else 0)),
        amount_paid=round_to_cents(due.expected_amount * (D("1.021") if late else D("1"))),
    )


def _payments(s: Seeder) -> None:
    props = s.session.query(Property).filter(Property.user_id == s.user.id).all()
    expenses = [to_expense_rule(e, p.is_active) for p in props for e in p.expenses]
    financings = [to_financing_rule(f, p.is_active) for p in props for f in p.financings]
    start = s.today - timedelta(days=PAYMENT_HISTORY_DAYS)
    past_dues = dues_in_period(expenses, financings, start, s.today)
    for index, due in enumerate(past_dues):
        decision = _payment_decision(due, index, s.today)
        if decision != "skip":
            s.add(_payment_for(due, decision, s.today))


def seed(session: Session, today: date) -> User:
    user = register_user(session, DEMO_EMAIL, DEMO_PASSWORD)
    seeder = Seeder(session, user, today)
    for build in (_apartment, _beach_house, _land, _office, _garage_and_sold):
        build(seeder)
    _payments(seeder)
    session.commit()
    return user


def main() -> None:
    database_url = Config().database_url
    if "demo" not in database_url:
        raise NotADemoDatabase(f"recusado: {database_url} não é um banco de demonstração")
    engine = create_engine_with_pragmas(database_url)
    with make_session_factory(engine)() as session:
        seed(session, clock.today())
    engine.dispose()
    print(f"Demo pronto: {DEMO_EMAIL} / {DEMO_PASSWORD}")


if __name__ == "__main__":
    main()
