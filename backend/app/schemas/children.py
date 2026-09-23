"""Entradas dos registros ligados a um imóvel: avaliação, financiamento, saldo e despesa."""

from __future__ import annotations

from pydantic import model_validator

from app.models.enums import (
    AmortizationSystem,
    ExpenseType,
    Frequency,
    InterestIndex,
    ValuationSource,
)
from app.schemas.common import (
    Cents,
    DueDay,
    InputModel,
    IsoDate,
    OptionalText50,
    PositiveInt,
    Rate,
    RequiredText100,
    RequiredText200,
    StrictBool,
)
from app.services.dues import due_date_in_month


class ValuationIn(InputModel):
    valuation_date: IsoDate
    value_cents: Cents
    source: ValuationSource


class FinancingIn(InputModel):
    lender: RequiredText100
    contract_number: OptionalText50 = None
    financed_amount_cents: Cents
    amortization_system: AmortizationSystem
    annual_interest_rate: Rate
    interest_index: InterestIndex
    term_months: PositiveInt
    first_installment_date: IsoDate
    due_day: DueDay
    current_installment_cents: Cents
    is_paid_off: StrictBool = False

    @model_validator(mode="after")
    def _first_installment_on_due_day(self) -> FinancingIn:
        first = self.first_installment_date
        if first != due_date_in_month(first.year, first.month, self.due_day):
            raise ValueError(
                "a 1ª parcela deve cair no dia de vencimento "
                "(ou no último dia do mês, se o mês for mais curto)"
            )
        return self


class BalanceIn(InputModel):
    balance_date: IsoDate
    balance_cents: Cents


class ExpenseIn(InputModel):
    expense_type: ExpenseType
    description: RequiredText200
    amount_cents: Cents
    frequency: Frequency
    due_day: DueDay
    start_date: IsoDate
    end_date: IsoDate | None = None
    installment_count: PositiveInt | None = None
    is_active: StrictBool = True

    @model_validator(mode="after")
    def _end_not_before_start(self) -> ExpenseIn:
        if self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("a data de fim não pode ser anterior à data de início")
        return self


# Campos que definem quando os vencimentos caem: travados depois do 1º pagamento (ESCOPO 3.5).
EXPENSE_RULE_FIELDS = frozenset({"frequency", "due_day", "start_date", "installment_count"})
FINANCING_RULE_FIELDS = frozenset({"due_day", "first_installment_date"})
