from pathlib import Path

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

import app.models  # noqa: F401  (registra todos os modelos no metadata)
from app.db import Base
from tests.migrations_helpers import alembic_config


def _schema_diff(database_url: str) -> list[object]:
    engine = create_engine(database_url)
    with engine.connect() as connection:
        diff = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    engine.dispose()
    return diff


def _tables(database_url: str) -> set[str]:
    engine = create_engine(database_url)
    tables = set(inspect(engine).get_table_names())
    engine.dispose()
    return tables


def test_upgrade_from_scratch_matches_models(tmp_path: Path, monkeypatch) -> None:
    config = alembic_config(tmp_path, monkeypatch)
    url = f"sqlite:///{tmp_path / 'app.db'}"

    command.upgrade(config, "head")

    assert _schema_diff(url) == []


def test_downgrade_last_then_upgrade_again(tmp_path: Path, monkeypatch) -> None:
    config = alembic_config(tmp_path, monkeypatch)
    url = f"sqlite:///{tmp_path / 'app.db'}"
    command.upgrade(config, "head")

    command.downgrade(config, "-1")
    assert "payments" not in _tables(url)
    assert "users" in _tables(url)

    command.upgrade(config, "head")
    assert _schema_diff(url) == []


def test_full_downgrade_to_base(tmp_path: Path, monkeypatch) -> None:
    config = alembic_config(tmp_path, monkeypatch)
    url = f"sqlite:///{tmp_path / 'app.db'}"
    command.upgrade(config, "head")

    command.downgrade(config, "base")

    assert _tables(url) <= {"alembic_version"}


def test_single_head(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    script = ScriptDirectory.from_config(alembic_config(tmp_path, monkeypatch))

    assert len(script.get_heads()) == 1
