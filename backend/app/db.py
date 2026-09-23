from __future__ import annotations

from collections.abc import Callable
from sqlite3 import Connection

from flask import current_app, g
from sqlalchemy import Engine, MetaData, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


def _pragma_listener(foreign_keys: bool) -> Callable[[Connection, object], None]:
    def _apply_sqlite_pragmas(dbapi_connection: Connection, connection_record: object) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute(f"PRAGMA foreign_keys={'ON' if foreign_keys else 'OFF'}")
        cursor.close()

    return _apply_sqlite_pragmas


def create_engine_with_pragmas(database_url: str, *, foreign_keys: bool = True) -> Engine:
    """Engine SQLite com WAL, busy_timeout e chaves estrangeiras (sem elas o SQLite as ignora).

    `foreign_keys=False` só para migrações: o modo batch do Alembic recria tabelas.
    """
    engine = create_engine(database_url, future=True)
    event.listen(engine, "connect", _pragma_listener(foreign_keys))
    return engine


def make_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_session() -> Session:
    """Sessão por requisição, guardada em flask.g e fechada no teardown."""
    if "db_session" not in g:
        factory = current_app.extensions["db_session_factory"]
        g.db_session = factory()
    return g.db_session
