from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ValuationSource, enum_type
from app.models.types import MoneyCents

if TYPE_CHECKING:
    from app.models.property import Property


class MarketValuation(Base):
    __tablename__ = "market_valuations"
    __table_args__ = (CheckConstraint("value_cents >= 0", name="value_non_negative"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), index=True
    )
    valuation_date: Mapped[date] = mapped_column(Date)
    value: Mapped[Decimal] = mapped_column("value_cents", MoneyCents())
    source: Mapped[ValuationSource] = mapped_column(enum_type(ValuationSource, "valuation_source"))

    property: Mapped[Property] = relationship(back_populates="valuations")
