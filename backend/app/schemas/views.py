from __future__ import annotations

from typing import Annotated

from pydantic import Field, model_validator

from app.schemas.common import InputModel, IsoDate

MAX_PERIOD_DAYS = 366


class MonthQuery(InputModel):
    year: Annotated[int, Field(ge=2000, le=2100)] | None = None
    month: Annotated[int, Field(ge=1, le=12)] | None = None

    @model_validator(mode="after")
    def _both_or_none(self) -> MonthQuery:
        if (self.year is None) != (self.month is None):
            raise ValueError("informe year e month juntos, ou nenhum dos dois")
        return self


class PeriodQuery(InputModel):
    start: IsoDate
    end: IsoDate

    @model_validator(mode="after")
    def _valid_period(self) -> PeriodQuery:
        if self.end < self.start:
            raise ValueError("end não pode ser anterior a start")
        if (self.end - self.start).days >= MAX_PERIOD_DAYS:
            raise ValueError(f"período máximo de {MAX_PERIOD_DAYS} dias")
        return self
