from __future__ import annotations

from typing import Annotated

from pydantic import Field

from app.schemas.common import Cents, InputModel, IsoDate
from app.services.dues import SourceKind


class PaymentCreateIn(InputModel):
    source_kind: SourceKind
    source_id: Annotated[int, Field(strict=True, ge=1)]
    reference_due_date: IsoDate
    payment_date: IsoDate
    amount_paid_cents: Cents


class PaymentUpdateIn(InputModel):
    """Só data e valor mudam; para trocar o vencimento, exclua e registre de novo."""

    payment_date: IsoDate
    amount_paid_cents: Cents
