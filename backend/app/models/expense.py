from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ExpenseType, Frequency, enum_type
from app.models.types import MoneyCents

if TYPE_CHECKING:
    from app.models.payment import Payment
    from app.models.property import Property


class RecurringExpense(Base):
    __tablename__ = "recurring_expenses"
    __table_args__ = (
        CheckConstraint("due_day BETWEEN 1 AND 31", name="due_day_range"),
        CheckConstraint("amount_cents >= 0", name="amount_non_negative"),
        CheckConstraint(
            "installment_count IS NULL OR installment_count > 0", name="installments_positive"
        ),
        CheckConstraint("end_date IS NULL OR end_date >= start_date", name="end_after_start"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )
    expense_type: Mapped[ExpenseType] = mapped_column(enum_type(ExpenseType, "expense_type"))
    description: Mapped[str] = mapped_column(String(200))
    amount: Mapped[Decimal] = mapped_column("amount_cents", MoneyCents())
    frequency: Mapped[Frequency] = mapped_column(enum_type(Frequency, "frequency"))
    due_day: Mapped[int]
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    installment_count: Mapped[int | None]
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())

    property: Mapped[Property] = relationship(back_populates="expenses")
    payments: Mapped[list[Payment]] = relationship(
        back_populates="recurring_expense", cascade="all, delete-orphan", passive_deletes=True
    )
