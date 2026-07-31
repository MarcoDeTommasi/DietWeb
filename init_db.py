"""Initialise the configured database without creating demo accounts."""

from dietapp.database import init_database


if __name__ == "__main__":
    init_database()
    print("Database inizializzato.")
