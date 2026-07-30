from __future__ import annotations

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from dietapp.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254))
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    dieta: Mapped[str | None] = mapped_column(Text)
    lista_alimenti: Mapped[str | None] = mapped_column(Text)


class StoricoSpesa(Base):
    __tablename__ = "storico_spesa"
    __table_args__ = (
        Index("ix_storico_spesa_username_data", "username", "data"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("users.username", ondelete="CASCADE"),
        nullable=False,
    )
    # Kept as ISO YYYY-MM-DD text for compatibility with the existing database.
    data: Mapped[str] = mapped_column(String(10), nullable=False)
    lista_spesa: Mapped[str] = mapped_column(Text, nullable=False)
