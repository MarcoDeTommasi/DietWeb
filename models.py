from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, JSON


# Modello per la tabella `users`
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    dieta = Column(Text, nullable=True)
    lista_alimenti = Column(Text, nullable=True)
    
# Modello per la tabella `storico_spesa`
class StoricoSpesa(Base):
    __tablename__ = "storico_spesa"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    data = Column(String, nullable=False)
    lista_spesa = Column(Text, nullable=False)