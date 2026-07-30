from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from dietapp.database import Base
from dietapp.models import StoricoSpesa, User
from dietapp.security import hash_password, is_password_hash


def normalise_url(value: str) -> str:
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg2://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg2://", 1)
    return value


def validate_json(value: str | None, expected: type) -> str | None:
    if value is None:
        return None
    decoded = json.loads(value)
    if not isinstance(decoded, expected):
        raise ValueError(f"JSON incompatibile: atteso {expected.__name__}")
    return json.dumps(decoded, ensure_ascii=False)


def migrate(source_path: Path, target_url: str) -> tuple[int, int]:
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if not target_url.startswith(("postgres://", "postgresql://")):
        raise ValueError("La destinazione deve essere un database PostgreSQL.")

    target_engine = create_engine(
        normalise_url(target_url),
        pool_pre_ping=True,
        connect_args={"connect_timeout": 10},
    )
    Base.metadata.create_all(target_engine)
    copied_users = 0
    copied_purchases = 0

    with sqlite3.connect(source_path) as source:
        source.row_factory = sqlite3.Row
        user_rows = source.execute("SELECT * FROM users ORDER BY id").fetchall()
        purchase_rows = source.execute(
            "SELECT * FROM storico_spesa ORDER BY id"
        ).fetchall()

    with Session(target_engine) as target:
        try:
            canonical_usernames: dict[str, str] = {}
            for row in user_rows:
                existing = target.scalar(
                    select(User).where(
                        func.lower(User.username) == row["username"].lower()
                    )
                )
                if existing:
                    canonical_usernames[row["username"]] = existing.username
                    continue
                user = User(
                    username=row["username"],
                    password=(
                        row["password"]
                        if is_password_hash(row["password"])
                        else hash_password(row["password"])
                    ),
                    email=row["email"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    dieta=validate_json(row["dieta"], dict),
                    lista_alimenti=validate_json(row["lista_alimenti"], list),
                )
                target.add(user)
                canonical_usernames[row["username"]] = user.username
                copied_users += 1
            target.flush()

            for row in purchase_rows:
                username = canonical_usernames.get(row["username"])
                if not username:
                    continue
                already_exists = target.scalar(
                    select(StoricoSpesa.id).where(
                        StoricoSpesa.username == username,
                        StoricoSpesa.data == row["data"],
                        StoricoSpesa.lista_spesa
                        == validate_json(row["lista_spesa"], dict),
                    )
                )
                if already_exists:
                    continue
                target.add(
                    StoricoSpesa(
                        username=username,
                        data=row["data"],
                        lista_spesa=validate_json(row["lista_spesa"], dict),
                    )
                )
                copied_purchases += 1
            target.commit()
        except Exception:
            target.rollback()
            raise
    target_engine.dispose()
    return copied_users, copied_purchases


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copia gli utenti e lo storico da SQLite a PostgreSQL."
    )
    parser.add_argument("source", type=Path, help="Percorso del file SQLite")
    parser.add_argument("--target-url", required=True, help="Connection string PostgreSQL")
    args = parser.parse_args()
    users, purchases = migrate(args.source.resolve(), args.target_url)
    print(f"Migrazione completata: {users} utenti, {purchases} acquisti copiati.")


if __name__ == "__main__":
    main()
