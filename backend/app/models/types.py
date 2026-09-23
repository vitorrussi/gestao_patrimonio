"""Tipos de coluna: Decimal no Python, inteiro no banco (sem float em nenhuma camada)."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Dialect, Integer
from sqlalchemy.types import TypeDecorator

from app.services.money import from_cents, from_scaled_int, to_cents, to_scaled_int


class MoneyCents(TypeDecorator[Decimal]):
    """Dinheiro: centavos (INTEGER) no banco, Decimal em reais no Python."""

    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: Decimal | None, dialect: Dialect) -> int | None:
        return None if value is None else to_cents(value)

    def process_result_value(self, value: int | None, dialect: Dialect) -> Decimal | None:
        return None if value is None else from_cents(value)


class ScaledDecimal(TypeDecorator[Decimal]):
    """Decimal com `scale` casas gravado como INTEGER (ex.: 33,3333% -> 333333)."""

    impl = Integer
    cache_ok = True

    def __init__(self, scale: int) -> None:
        super().__init__()
        self.scale = scale

    def process_bind_param(self, value: Decimal | None, dialect: Dialect) -> int | None:
        return None if value is None else to_scaled_int(value, self.scale)

    def process_result_value(self, value: int | None, dialect: Dialect) -> Decimal | None:
        return None if value is None else from_scaled_int(value, self.scale)
