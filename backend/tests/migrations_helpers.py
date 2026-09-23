from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig

BACKEND_DIR = Path(__file__).resolve().parents[1]


def alembic_config(data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> AlembicConfig:
    """Config do Alembic apontando para um SQLite temporário (o env.py lê DATA_DIR)."""
    monkeypatch.setenv("DATA_DIR", str(data_dir))
    monkeypatch.delenv("DATABASE_URL", raising=False)
    config = AlembicConfig(str(BACKEND_DIR / "alembic.ini"))
    config.attributes["configure_logger"] = False
    return config


def upgrade_to_head(data_dir: Path, monkeypatch: pytest.MonkeyPatch) -> str:
    """Aplica todas as migrações e devolve a URL do banco."""
    command.upgrade(alembic_config(data_dir, monkeypatch), "head")
    return f"sqlite:///{data_dir / 'app.db'}"
