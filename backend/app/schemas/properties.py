from __future__ import annotations

import re
from decimal import Decimal
from typing import Annotated

from pydantic import BeforeValidator

from app.models.enums import AcquisitionMethod, PropertyType, PropertyUsage
from app.schemas.common import (
    Cents,
    InputModel,
    IsoDate,
    OptionalText20,
    OptionalText50,
    OptionalText100,
    OptionalText150,
    OptionalText200,
    Percent,
    RequiredText100,
    StrictBool,
)


def _normalize_state(value: object) -> object:
    if isinstance(value, str) and value.strip():
        state = value.strip().upper()
        if not re.fullmatch(r"[A-Z]{2}", state):
            raise ValueError("UF com 2 letras, ex.: SC")
        return state
    return None if isinstance(value, str) else value


def _normalize_zip(value: object) -> object:
    if isinstance(value, str) and value.strip():
        digits = value.strip()
        if not re.fullmatch(r"\d{5}-?\d{3}", digits):
            raise ValueError("CEP no formato 00000-000")
        digits = digits.replace("-", "")
        return f"{digits[:5]}-{digits[5:]}"
    return None if isinstance(value, str) else value


StateCode = Annotated[str | None, BeforeValidator(_normalize_state)]
ZipCode = Annotated[str | None, BeforeValidator(_normalize_zip)]


class PropertyIn(InputModel):
    nickname: RequiredText100
    property_type: PropertyType
    usage: PropertyUsage
    street: OptionalText200 = None
    number: OptionalText20 = None
    complement: OptionalText100 = None
    neighborhood: OptionalText100 = None
    city: OptionalText100 = None
    state: StateCode = None
    zip_code: ZipCode = None
    registration_number: OptionalText50 = None
    registry_office: OptionalText150 = None
    municipal_registration: OptionalText50 = None
    ownership_percentage: Percent = Decimal("100")
    acquisition_date: IsoDate | None = None
    acquisition_method: AcquisitionMethod | None = None
    purchase_price_cents: Cents = 0
    itbi_cents: Cents = 0
    deed_registration_cents: Cents = 0
    is_active: StrictBool = True
