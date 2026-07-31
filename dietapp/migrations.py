from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from dietapp.models import User
from dietapp.security import hash_password, is_password_hash


def migrate_legacy_passwords(db: Session) -> int:
    """Hash passwords left in plaintext by versions older than 1.0."""
    migrated = 0
    for user in db.scalars(select(User)).all():
        if not is_password_hash(user.password):
            user.password = hash_password(user.password)
            migrated += 1
    return migrated
