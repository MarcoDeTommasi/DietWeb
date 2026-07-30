from __future__ import annotations

import re

import bcrypt


USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,64}$")
BCRYPT_PREFIXES = ("$2a$", "$2b$", "$2y$")
DUMMY_PASSWORD_HASH = bcrypt.hashpw(
    b"dietapp-dummy-password", bcrypt.gensalt()
).decode("utf-8")


def normalise_username(username: str) -> str:
    return username.strip().lower()


def validate_username(username: str) -> str | None:
    if not USERNAME_PATTERN.fullmatch(username):
        return (
            "Lo username deve avere 3–64 caratteri e può contenere solo "
            "lettere, numeri, punto, trattino e underscore."
        )
    return None


def validate_password(password: str) -> str | None:
    if len(password) < 8:
        return "La password deve contenere almeno 8 caratteri."
    if len(password.encode("utf-8")) > 72:
        return "La password non può superare 72 byte."
    if not any(character.isalpha() for character in password):
        return "La password deve contenere almeno una lettera."
    if not any(character.isdigit() for character in password):
        return "La password deve contenere almeno un numero."
    return None


def hash_password(password: str) -> str:
    if len(password.encode("utf-8")) > 72:
        raise ValueError("bcrypt supporta password fino a 72 byte")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def is_password_hash(value: str) -> bool:
    return value.startswith(BCRYPT_PREFIXES)


def verify_password(password: str, stored_password: str) -> bool:
    if not is_password_hash(stored_password):
        # Compatibility path; the repository migrates a successful match immediately.
        return password == stored_password
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"), stored_password.encode("utf-8")
        )
    except ValueError:
        return False
