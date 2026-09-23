from __future__ import annotations

from datetime import UTC, date, datetime, timedelta, timezone

# Horário de Brasília. Offset fixo: o Brasil não tem horário de verão desde 2019,
# e a imagem Docker roda em UTC (sem isso, algo "atrasaria" às 21h do próprio dia).
BRASILIA = timezone(timedelta(hours=-3), "BRT")


def today() -> date:
    return datetime.now(UTC).astimezone(BRASILIA).date()
