from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.types import MoneyCents

if TYPE_CHECKING:
    from app.models.expense import RecurringExpense
    from app.models.financing import Financing


class Payment(Base):
    """Quita um vencimento calculado: origem (despesa OU financiamento) + data de referência."""

    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint(
            "(recurring_expense_id IS NULL) <> (financing_id IS NULL)", name="exactly_one_source"
        ),
        CheckConstraint("amount_paid_cents >= 0", name="amount_non_negative"),
        # NULLs são distintos no UNIQUE: cada par só vale para o tipo de origem preenchido.
        UniqueConstraint("recurring_expense_id", "reference_due_date"),
        UniqueConstraint("financing_id", "reference_due_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    recurring_expense_id: Mapped[int | None] = mapped_column(
        ForeignKey("recurring_expenses.id", ondelete="CASCADE"), index=True
    )
    financing_id: Mapped[int | None] = mapped_column(
        ForeignKey("financings.id", ondelete="CASCADE"), index=True
    )
    reference_due_date: Mapped[date] = mapped_column(Date)
    payment_date: Mapped[date] = mapped_column(Date)
    amount_paid: Mapped[Decimal] = mapped_column("amount_paid_cents", MoneyCents())

    recurring_expense: Mapped[RecurringExpense | None] = relationship(back_populates="payments")
    financing: Mapped[Financing | None] = relationship(back_populates="payments")
