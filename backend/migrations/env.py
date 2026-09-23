import sys
from logging.config import fileConfig
from pathlib import Path
from typing import Any, Literal

from alembic import context
from sqlalchemy import text
from sqlalchemy.types import TypeDecorator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import Config  # noqa: E402
from app.db import Base, create_engine_with_pragmas  # noqa: E402
from app.models import AppMeta  # noqa: E402,F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Os testes desligam isso para o Alembic não reconfigurar o logging do pytest.
if config.config_file_name is not None and config.attributes.get("configure_logger", True):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

app_config = Config()
config.set_main_option("sqlalchemy.url", app_config.database_url)


def render_item(type_: str, obj: Any, autogen_context: Any) -> str | Literal[False]:
    """Tipos próprios (MoneyCents, ScaledDecimal) viram o tipo do banco na migração.

    Assim as migrações não importam código do app, que pode mudar depois.
    """
    if type_ == "type" and isinstance(obj, TypeDecorator):
        return f"sa.{obj.impl_instance!r}"
    return False


def run_migrations_offline() -> None:
    """Roda as migrações em modo 'offline' (só gera SQL, sem conectar)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def _assert_foreign_keys_consistent(connection: Any) -> None:
    violations = connection.execute(text("PRAGMA foreign_key_check")).fetchall()
    if violations:
        raise RuntimeError(f"Migração deixou chaves estrangeiras inválidas: {violations}")


def run_migrations_online() -> None:
    """Roda as migrações conectando ao banco.

    Chaves estrangeiras ficam desligadas durante a migração (o modo batch recria tabelas)
    e a consistência é conferida no fim.
    """
    connectable = create_engine_with_pragmas(app_config.database_url, foreign_keys=False)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            render_item=render_item,
        )

        with context.begin_transaction():
            context.run_migrations()

        _assert_foreign_keys_consistent(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
