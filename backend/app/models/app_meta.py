from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AppMeta(Base):
    """Tabela neutra usada só para o health check provar leitura do banco."""

    __tablename__ = "app_meta"

    id: Mapped[int] = mapped_column(primary_key=True)
    chave: Mapped[str] = mapped_column(String(100), unique=True)
    valor: Mapped[str] = mapped_column(String(255))
