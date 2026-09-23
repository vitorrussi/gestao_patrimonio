"""Conversões exatas entre Decimal e inteiros escalados (centavos no banco)."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CENTS_SCALE = 2
CENT = Decimal("0.01")


class InexactDecimalError(ValueError):
    """O valor tem mais casas decimais do que a escala permite."""


def to_scaled_int(value: Decimal, scale: int) -> int:
    """Decimal -> inteiro com `scale` casas implícitas. Nunca arredonda."""
    if not isinstance(value, Decimal):
        raise TypeError(f"esperado Decimal, recebido {type(value).__name__}")
    if not value.is_finite():
        raise InexactDecimalError(f"valor não finito: {value}")
    scaled = value.scaleb(scale)
    if scaled != scaled.to_integral_value():
        raise InexactDecimalError(f"{value} tem mais de {scale} casas decimais")
    return int(scaled)


def from_scaled_int(value: int, scale: int) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"esperado int, recebido {type(value).__name__}")
    return Decimal(value).scaleb(-scale)


def to_cents(value: Decimal) -> int:
    return to_scaled_int(value, CENTS_SCALE)


def from_cents(cents: int) -> Decimal:
    return from_scaled_int(cents, CENTS_SCALE)


def round_to_cents(value: Decimal) -> Decimal:
    """Arredonda para centavos (meio para cima). Usar só no fim de um cálculo."""
    return value.quantize(CENT, rounding=ROUND_HALF_UP)
