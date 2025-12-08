
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User, StoricoSpesa
import json
from database import get_db


def get_user_diet(db: Session, username: str):
    """
    Recupera la dieta di un utente dal database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and user.dieta:
        return json.loads(user.dieta)
    return None


def get_user_food_list(db: Session, username: str):
    """
    Recupera la lista degli alimenti di un utente dal database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and user.lista_alimenti:
        return json.loads(user.lista_alimenti)
    return None


def get_user_name(db: Session, username: str):
    """
    Recupera il nome e il cognome di un utente dal database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        return user.first_name, user.last_name
    return None, None


def get_user_spesa(db: Session, username: str):
    """
    Recupera la lista della spesa di un utente dal database.
    """
    spese = db.query(StoricoSpesa).filter(StoricoSpesa.username == username).order_by(StoricoSpesa.data.desc()).all()
    if spese:
        return [{"lista_spesa": json.loads(spesa.lista_spesa), "data": spesa.data} for spesa in spese]
    return []


def save_diet(db: Session, username: str, dieta_dict: dict):
    """
    Registra o aggiorna la dieta di un utente nel database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.dieta = json.dumps(dieta_dict)
        db.commit()
        db.refresh(user)
        return True
    return False


def save_food_list(db: Session, username: str, food_list: list):
    """
    Registra o aggiorna la lista degli alimenti di un utente nel database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.lista_alimenti = json.dumps(food_list)
        db.commit()
        db.refresh(user)
        return True
    return False


def save_spesa(db: Session, username: str, data: str, spesa: dict):
    """
    Salva una nuova lista della spesa per un utente.
    """
    try:
        nuova_spesa = StoricoSpesa(
            username=username,
            data=data,
            lista_spesa=json.dumps(spesa)
        )
        db.add(nuova_spesa)
        db.commit()
        db.refresh(nuova_spesa)
        return True
    except IntegrityError:
        db.rollback()
        return False


def update_password(db: Session, username: str, new_password: str):
    """
    Aggiorna la password di un utente nel database.
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.password = new_password  # Assicurati di hashare la password prima di salvarla
        db.commit()
        db.refresh(user)
        return True
    return False


def register_user(db: Session, username: str, first_name: str, last_name: str, email: str, password: str):
    """
    Registra un nuovo utente nel database.
    """
    try:
        new_user = User(
            username=username,
            password=password,  # Assicurati di hashare la password prima di salvarla
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True
    except IntegrityError:
        db.rollback()
        return False


def authenticate_user(db: Session, username: str, password: str):
    """
    Verifica se l'username e la password forniti sono validi.
    """
    user = db.query(User).filter(User.username == username).first()
    if user and user.password == password:  # Assicurati di confrontare gli hash delle password
        return True
    return False
