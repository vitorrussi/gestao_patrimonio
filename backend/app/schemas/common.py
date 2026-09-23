"""Tipos de campo da API e conversão ORM <-> formato da API.

Convenção: dinheiro vai como inteiro em centavos em campos `*_cents`; percentuais e
taxas vão como texto decimal. `float` é recusado em ambos (regra 1).
"""

from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
)

from app.services.money import from_cents, to_cents

MAX_CENTS = 10**13  # R$ 100 bilhões: folga grande e longe do limite do INTEGER do SQLite
CENTS_SUFFIX = "_cents"


def _reject_float(value: object) -> object:
    if isinstance(value, float):
        raise ValueError('use texto para valores decimais, ex.: "50.00"')
    return value


def _four_places(value: Decimal) -> Decimal:
    """Formato canônico ("50" -> "50.0000"): a resposta não muda entre criar e reler."""
    return value.quantize(Decimal("0.0001"))


def _require_iso_date(value: object) -> object:
    if isinstance(value, date) or (
        isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)
    ):
        return value
    raise ValueError("data no formato AAAA-MM-DD")


def _blank_to_none(value: object) -> object:
    if isinstance(value, str) and value.strip() == "":
        return None
    return value


Cents = Annotated[int, Field(strict=True, ge=0, le=MAX_CENTS)]
Percent = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    Field(ge=0, le=100, max_digits=7, decimal_places=4),
    AfterValidator(_four_places),
]
Rate = Annotated[
    Decimal,
    BeforeValidator(_reject_float),
    Field(ge=0, le=1000, max_digits=8, decimal_places=4),
    AfterValidator(_four_places),
]
IsoDate = Annotated[date, BeforeValidator(_require_iso_date)]
StrictBool = Annotated[bool, Field(strict=True)]
DueDay = Annotated[int, Field(strict=True, ge=1, le=31)]
PositiveInt = Annotated[int, Field(strict=True, ge=1, le=1200)]


def _text(max_length: int, min_length: int = 0) -> Any:
    return StringConstraints(strip_whitespace=True, min_length=min_length, max_length=max_length)


RequiredText100 = Annotated[str, _text(100, min_length=1)]
RequiredText200 = Annotated[str, _text(200, min_length=1)]
OptionalText20 = Annotated[Annotated[str, _text(20)] | None, BeforeValidator(_blank_to_none)]
OptionalText50 = Annotated[Annotated[str, _text(50)] | None, BeforeValidator(_blank_to_none)]
OptionalText100 = Annotated[Annotated[str, _text(100)] | None, BeforeValidator(_blank_to_none)]
OptionalText150 = Annotated[Annotated[str, _text(150)] | None, BeforeValidator(_blank_to_none)]
OptionalText200 = Annotated[Annotated[str, _text(200)] | None, BeforeValidator(_blank_to_none)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True)


# --- conversão ORM <-> API ---


def _api_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, date):
        return value.isoformat()
    return value


def orm_to_api(obj: object, model: type[BaseModel]) -> dict[str, Any]:
    """Campos de `model` lidos do objeto ORM, no formato JSON da API."""
    data: dict[str, Any] = {}
    for name in model.model_fields:
        if name.endswith(CENTS_SUFFIX):
            value = getattr(obj, name.removesuffix(CENTS_SUFFIX))
            data[name] = None if value is None else to_cents(value)
        else:
            data[name] = _api_value(getattr(obj, name))
    return data


def api_to_orm(validated: BaseModel, obj: object) -> None:
    """Copia todos os campos validados para o objeto ORM (centavos -> Decimal)."""
    for name in type(validated).model_fields:
        value = getattr(validated, name)
        if name.endswith(CENTS_SUFFIX):
            setattr(
                obj, name.removesuffix(CENTS_SUFFIX), None if value is None else from_cents(value)
            )
        else:
            setattr(obj, name, value)


def cents_or_none(value: Decimal | None) -> int | None:
    return None if value is None else to_cents(value)
