"""Backward-compatible database imports.

New code should import from :mod:`dietapp.database`.
"""

from dietapp.database import (
    Base,
    SessionLocal,
    engine,
    get_db,
    init_database,
    session_scope,
)

__all__ = [
    "Base",
    "SessionLocal",
    "engine",
    "get_db",
    "init_database",
    "session_scope",
]
