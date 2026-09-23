from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Date, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import AcquisitionMethod, PropertyType, PropertyUsage, enum_type
from app.models.types import MoneyCents, ScaledDecimal

if TYPE_CHECKING:
    from app.models.expense import RecurringExpense
    from app.models.financing import Financing
    from app.models.valuation import MarketValuation

PERCENT_SCALE = 4


class Property(Base):
    __tablename__ = "properties"
    __table_args__ = (
        CheckConstraint(
            "ownership_percentage_x10000 BETWEEN 0 AND 1000000", name="ownership_range"
        ),
        CheckConstraint(
            "purchase_price_cents >= 0 AND itbi_cents >= 0 AND deed_registration_cents >= 0",
            name="acquisition_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)

    nickname: Mapped[str] = mapped_column(String(100))
    property_type: Mapped[PropertyType] = mapped_column(enum_type(PropertyType, "property_type"))
    usage: Mapped[PropertyUsage] = mapped_column(enum_type(PropertyUsage, "property_usage"))

    street: Mapped[str | None] = mapped_column(String(200))
    number: Mapped[str | None] = mapped_column(String(20))
    complement: Mapped[str | None] = mapped_column(String(100))
    neighborhood: Mapped[str | None] = mapped_column(String(100))
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(2))
    zip_code: Mapped[str | None] = mapped_column(String(9))

    registration_number: Mapped[str | None] = mapped_column(String(50))
    registry_office: Mapped[str | None] = mapped_column(String(150))
    municipal_registration: Mapped[str | None] = mapped_column(String(50))

    ownership_percentage: Mapped[Decimal] = mapped_column(
        "ownership_percentage_x10000",
        ScaledDecimal(PERCENT_SCALE),
        default=Decimal("100"),
        server_default="1000000",
    )
    acquisition_date: Mapped[date | None] = mapped_column(Date)
    acquisition_method: Mapped[AcquisitionMethod | None] = mapped_column(
        enum_type(AcquisitionMethod, "acquisition_method")
    )
    purchase_price: Mapped[Decimal] = mapped_column(
        "purchase_price_cents", MoneyCents(), default=Decimal("0"), server_default="0"
    )
    itbi: Mapped[Decimal] = mapped_column(
        "itbi_cents", MoneyCents(), default=Decimal("0"), server_default="0"
    )
    deed_registration: Mapped[Decimal] = mapped_column(
        "deed_registration_cents", MoneyCents(), default=Decimal("0"), server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(default=True, server_default=true())

    valuations: Mapped[list[MarketValuation]] = relationship(
        back_populates="property", cascade="all, delete-orphan", passive_deletes=True
    )
    financings: Mapped[list[Financing]] = relationship(
        back_populates="property", cascade="all, delete-orphan", passive_deletes=True
    )
    expenses: Mapped[list[RecurringExpense]] = relationship(
        back_populates="property", cascade="all, delete-orphan", passive_deletes=True
    )
