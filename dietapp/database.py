from __future__ import annotations

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from dietapp.config import get_settings


class Base(DeclarativeBase):
    pass


def create_database_engine(database_url: str) -> Engine:
    is_sqlite = database_url.startswith("sqlite")
    connect_args: dict[str, object] = (
        {"check_same_thread": False, "timeout": 20}
        if is_sqlite
        else {"connect_timeout": 10}
    )
    engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=not is_sqlite,
        pool_recycle=300 if not is_sqlite else -1,
    )

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = create_database_engine(get_settings().database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@contextmanager
def session_scope() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """Compatibility dependency for code that expects a generator."""
    with session_scope() as session:
        yield session


def init_database() -> None:
    # Importing registers all mappings on Base.metadata.
    from dietapp import models  # noqa: F401
    from dietapp.migrations import migrate_legacy_passwords

    Base.metadata.create_all(bind=engine)
    with session_scope() as session:
        if migrate_legacy_passwords(session):
            session.commit()
