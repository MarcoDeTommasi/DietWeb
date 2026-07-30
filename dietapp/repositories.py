from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from dietapp.models import StoricoSpesa, User
from dietapp.security import (
    DUMMY_PASSWORD_HASH,
    hash_password,
    is_password_hash,
    normalise_username,
    verify_password,
)


class RepositoryError(RuntimeError):
    pass


def _decode_json(value: Any, expected_type: type) -> Any:
    if value is None:
        return None
    decoded = value
    if isinstance(value, str):
        try:
            decoded = json.loads(value)
        except (TypeError, json.JSONDecodeError) as error:
            raise RepositoryError("I dati salvati nel database non sono validi.") from error
    if not isinstance(decoded, expected_type):
        raise RepositoryError("I dati salvati nel database hanno un formato inatteso.")
    return decoded


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError as error:
        db.rollback()
        raise RepositoryError("Operazione sul database non riuscita.") from error


def get_user(db: Session, username: str) -> User | None:
    return db.scalar(
        select(User).where(
            func.lower(User.username) == normalise_username(username)
        )
    )


def get_user_name(db: Session, username: str) -> tuple[str | None, str | None]:
    user = get_user(db, username)
    return (user.first_name, user.last_name) if user else (None, None)


def get_user_diet(db: Session, username: str) -> dict[str, Any] | None:
    user = get_user(db, username)
    return _decode_json(user.dieta, dict) if user and user.dieta else None


def get_user_food_list(db: Session, username: str) -> list[str] | None:
    user = get_user(db, username)
    return (
        _decode_json(user.lista_alimenti, list)
        if user and user.lista_alimenti
        else None
    )


def get_user_purchases(
    db: Session, username: str
) -> list[dict[str, Any]]:
    user = get_user(db, username)
    if not user:
        return []
    rows = db.scalars(
        select(StoricoSpesa)
        .where(StoricoSpesa.username == user.username)
        .order_by(StoricoSpesa.data.desc(), StoricoSpesa.id.desc())
    ).all()
    return [
        {
            "lista_spesa": _decode_json(row.lista_spesa, dict),
            "data": row.data,
            "id": row.id,
        }
        for row in rows
    ]


def register_user(
    db: Session,
    username: str,
    first_name: str,
    last_name: str,
    email: str,
    password: str,
) -> bool:
    user = User(
        username=normalise_username(username),
        password=hash_password(password),
        email=email.strip().lower() or None,
        first_name=first_name.strip() or None,
        last_name=last_name.strip() or None,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return False
    except SQLAlchemyError as error:
        db.rollback()
        raise RepositoryError("Registrazione non riuscita.") from error
    return True


def authenticate_user(db: Session, username: str, password: str) -> bool:
    user = get_user(db, username)
    if not user:
        # Keep the expensive password check to reduce username timing disclosure.
        verify_password(password, DUMMY_PASSWORD_HASH)
        return False
    if not verify_password(password, user.password):
        return False
    if not is_password_hash(user.password):
        user.password = hash_password(password)
        _commit(db)
    return True


def update_password(
    db: Session, username: str, current_password: str, new_password: str
) -> bool:
    user = get_user(db, username)
    if not user or not verify_password(current_password, user.password):
        return False
    user.password = hash_password(new_password)
    _commit(db)
    return True


def save_user_plan(
    db: Session, username: str, diet: Mapping[str, Any], food_list: list[str]
) -> bool:
    user = get_user(db, username)
    if not user:
        return False
    # One transaction prevents diet and food list from getting out of sync.
    user.dieta = json.dumps(diet, ensure_ascii=False)
    user.lista_alimenti = json.dumps(food_list, ensure_ascii=False)
    _commit(db)
    return True


def save_purchase(
    db: Session, username: str, date_iso: str, shopping: Mapping[str, Any]
) -> bool:
    user = get_user(db, username)
    if not user:
        return False
    db.add(
        StoricoSpesa(
            username=user.username,
            data=date_iso,
            lista_spesa=json.dumps(shopping, ensure_ascii=False),
        )
    )
    _commit(db)
    return True
