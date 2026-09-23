"""Patrimônio por imóvel e total. Funções puras: entrada em dataclasses, sem banco."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.models.enums import PropertyType
from app.services.money import round_to_cents

ZERO = Decimal("0.00")
HUNDRED = Decimal("100")


@dataclass(frozen=True)
class ValuationRecord:
    valuation_date: date
    value: Decimal
    record_id: int  # id do banco: desempata registros com a mesma data


@dataclass(frozen=True)
class BalanceRecord:
    balance_date: date
    balance: Decimal
    record_id: int  # id do banco: desempata registros com a mesma data


@dataclass(frozen=True)
class FinancingDebtInput:
    financed_amount: Decimal
    is_paid_off: bool = False
    balances: Sequence[BalanceRecord] = ()


@dataclass(frozen=True)
class DebtResult:
    amount: Decimal
    # True quando não há saldo lançado e o valor financiado é usado como estimativa.
    estimated: bool


@dataclass(frozen=True)
class PropertyInput:
    property_id: int
    property_type: PropertyType
    ownership_percentage: Decimal = HUNDRED
    is_active: bool = True
    valuations: Sequence[ValuationRecord] = ()
    financings: Sequence[FinancingDebtInput] = ()


@dataclass(frozen=True)
class PropertyEquity:
    property_id: int
    market_value: Decimal | None  # valor do imóvel inteiro (100%)
    gross: Decimal | None  # valor de mercado × participação; None = "sem valor"
    debt: Decimal
    net: Decimal | None
    debt_estimated: bool


@dataclass(frozen=True)
class PortfolioSummary:
    gross_total: Decimal
    debt_total: Decimal
    net_total: Decimal
    property_count: int
    count_by_type: dict[PropertyType, int]
    properties_without_value: int
    debt_estimated: bool


def acquisition_total(
    purchase_price: Decimal, itbi: Decimal, deed_registration: Decimal
) -> Decimal:
    """Valor total de aquisição no MVP (benfeitorias entram na Versão 2)."""
    return purchase_price + itbi + deed_registration


def current_market_value(valuations: Iterable[ValuationRecord]) -> Decimal | None:
    """Avaliação com a data mais recente; no empate, a cadastrada por último (maior id)."""
    latest = max(valuations, key=lambda v: (v.valuation_date, v.record_id), default=None)
    return None if latest is None else latest.value


def financing_debt(financing: FinancingDebtInput) -> DebtResult:
    if financing.is_paid_off:
        return DebtResult(ZERO, estimated=False)
    latest = max(financing.balances, key=lambda b: (b.balance_date, b.record_id), default=None)
    if latest is None:
        return DebtResult(financing.financed_amount, estimated=True)
    return DebtResult(latest.balance, estimated=False)


def property_equity(prop: PropertyInput) -> PropertyEquity:
    """Líquido = valor de mercado atual × participação − saldo devedor (ESCOPO, regra 2)."""
    debts = [financing_debt(f) for f in prop.financings]
    debt = sum((d.amount for d in debts), ZERO)
    market_value = current_market_value(prop.valuations)
    gross = None
    if market_value is not None:
        gross = round_to_cents(market_value * prop.ownership_percentage / HUNDRED)
    return PropertyEquity(
        property_id=prop.property_id,
        market_value=market_value,
        gross=gross,
        debt=debt,
        net=None if gross is None else gross - debt,
        debt_estimated=any(d.estimated for d in debts),
    )


def _valued(equities: list[PropertyEquity]) -> list[Decimal]:
    return [e.gross for e in equities if e.gross is not None]


def portfolio_summary(properties: Iterable[PropertyInput]) -> PortfolioSummary:
    """Totais só com imóveis ativos. Bruto total = soma dos brutos exibidos por imóvel."""
    active = [p for p in properties if p.is_active]
    equities = [property_equity(p) for p in active]
    valued = _valued(equities)
    gross_total = sum(valued, ZERO)
    debt_total = sum((e.debt for e in equities), ZERO)
    return PortfolioSummary(
        gross_total=gross_total,
        debt_total=debt_total,
        net_total=gross_total - debt_total,
        property_count=len(active),
        count_by_type=dict(Counter(p.property_type for p in active)),
        properties_without_value=len(equities) - len(valued),
        debt_estimated=any(e.debt_estimated for e in equities),
    )
