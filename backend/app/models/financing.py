from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import AmortizationSystem, InterestIndex, enum_type
from app.models.types import MoneyCents, ScaledDecimal

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.property import Property

RATE_SCALE = 4


class Financing(Base):
    __tablename__ = "financings"
    __table_args__ = (
        CheckConstraint("due_day BETWEEN 1 AND 31", name="due_day_range"),
        CheckConstraint("term_months > 0", name="term_positive"),
        CheckConstraint(
            "financed_amount_cents >= 0 AND current_installment_cents >= 0 "
            "AND annual_interest_rate_x10000 >= 0",
            name="values_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )
    lender: Mapped[str] = mapped_column(String(100))
    contract_number: Mapped[str | None] = mapped_column(String(50))
    financed_amount: Mapped[Decimal] = mapped_column("financed_amount_cents", MoneyCents())
    amortization_system: Mapped[AmortizationSystem] = mapped_column(
        enum_type(AmortizationSystem, "amortization_system")
    )
    annual_interest_rate: Mapped[Decimal] = mapped_column(
        "annual_interest_rate_x10000", ScaledDecimal(RATE_SCALE)
    )
    interest_index: Mapped[InterestIndex] = mapped_column(
        enum_type(InterestIndex, "interest_index")
    )
    term_months: Mapped[int]
    first_installment_date: Mapped[date] = mapped_column(Date)
    due_day: Mapped[int]
    current_installment: Mapped[Decimal] = mapped_column("current_installment_cents", MoneyCents())
    is_paid_off: Mapped[bool] = mapped_column(default=False, server_default=false())

    property: Mapped[Property] = relationship(back_populates="financings")
    balances: Mapped[list[DebtBalance]] = relationship(
        back_populates="financing", cascade="all, delete-orphan", passive_deletes=True
    )
    payments: Mapped[list[Payment]] = relationship(
        back_populates="financing", cascade="all, delete-orphan", passive_deletes=True
    )


class DebtBalance(Base):
    __tablename__ = "debt_balances"
    __table_args__ = (CheckConstraint("balance_cents >= 0", name="balance_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    financing_id: Mapped[int] = mapped_column(
        ForeignKey("financings.id", ondelete="CASCADE"), index=True
    )
    balance_date: Mapped[date] = mapped_column(Date)
    balance: Mapped[Decimal] = mapped_column("balance_cents", MoneyCents())

    financing: Mapped[Financing] = relationship(back_populates="balances")
