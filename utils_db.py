import sqlite3
import os
import json
import pandas as pd
from psycopg2 import OperationalError
import streamlit as st
import streamlit_authenticator as stauth
import psycopg2

# Configurazione per PostgreSQL (non usato in dev)
DB_CONFIG = {
    "dbname": "nome_database",
    "user": "nome_utente",
    "password": "password",
    "host": "localhost",
    "port": 5432
}

# Percorso per il database SQLite (fallback)
SQLITE_DB_PATH = "dieta.db"

def initialize_sqlite_db():
    """
    Crea il database SQLite e le tabelle necessarie se non esistono.
    """

    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()

    # Crea la tabella `users`
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT,
        first_name TEXT,
        last_name TEXT,
        dieta TEXT,
        lista_alimenti TEXT
    );
    """)

    # Crea la tabella `storico_spesa`
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS storico_spesa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        data TEXT NOT NULL,
        lista_spesa TEXT
    );
    """)

    conn.commit()
    conn.close()

def get_db_connection():
    """
    Restituisce una connessione al database PostgreSQL o SQLite come fallback.
    """
    try:
        # Prova a connetterti a PostgreSQL
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Connessione a PostgreSQL riuscita!")
        return conn
    except OperationalError:
        print("⚠️ PostgreSQL non disponibile. Uso SQLite come fallback.")
        # Se PostgreSQL non è disponibile, usa SQLite
        initialize_sqlite_db()  # Assicurati che il database SQLite sia inizializzato
        conn = sqlite3.connect(SQLITE_DB_PATH)
        return conn
    
def get_user_diet(username):
    """
    Recupera i dettagli di un singolo utente dal database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        # Recupera i dettagli dell'utente
        cursor.execute("""
            SELECT dieta
            FROM users
            WHERE username = ?
        """, (username,))
        result = cursor.fetchone()[0]

        if result:
            dieta = result
            return  dieta
        else:
            return None  # Utente non trovato
    except Exception as e:
        print(f"Errore durante il recupero dell'utente: {e}")
        return None
    finally:
        conn.close()

def get_user_food_list(username):
    """
    Recupera la lista degli alimenti di un singolo utente dal database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        # Recupera i dettagli dell'utente
        cursor.execute("""
            SELECT lista_alimenti
            FROM users
            WHERE username = ?
        """, (username,))
        result = cursor.fetchone()[0]

        if result:
            food_list_json = result
            food_list = json.loads(food_list_json)
            return  food_list
        else:
            return None  # Utente non trovato
    except Exception as e:
        print(f"Errore durante il recupero dell'utente: {e}")
        return None
    finally:
        conn.close()


def get_user_name(username):
    """
    Recupera i dettagli di un singolo utente dal database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        # Recupera i dettagli dell'utente
        cursor.execute("""
            SELECT first_name,last_name
            FROM users
            WHERE username = ?
        """, (username,))
        result = cursor.fetchone()

        if result:
            first_name, last_name = result
            return first_name, last_name
        else:
            return None, None  # Utente non trovato
    except Exception as e:
        print(f"Errore durante il recupero dell'utente: {e}")
        return None, None
    finally:
        conn.close()

def get_user_spesa(username):
    """
    recupera la lista della spesa di un utente dal database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
        SELECT lista_spesa, data
            FROM storico_spesa
            WHERE username = ?
            ORDER BY data DESC

        """, (username,))
        result = cursor.fetchall()

        if result:
            for index, details in enumerate(result):
                result[index] = [json.loads(details[0]), details[1]]
            return result
        else:
            return None  # Nessuna lista della spesa trovata
    except Exception as e:
        print(f"Errore durante il recupero della lista della spesa: {e}")
        return None
    finally:
        conn.close()

def update_password(username, new_password):
    """
    Aggiorna la password di un utente nel database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        if len(new_password) <= 7:
            return st.error("❌ La password deve essere di almeno 8 caratteri.")
        # Hash della nuova password
        new_password_hash = stauth.Hasher().hash(new_password)

        # Aggiorna la password nel database
        cursor.execute("""
            UPDATE users
            SET password = ?
            WHERE username = ?
        """, (new_password_hash, username))
        conn.commit()
    except Exception as e:
        print(f"Errore durante l'aggiornamento della password: {e}")
    finally:
        conn.close()

def save_diet(username, dieta_dict):
    """
    Registra o aggiorna la dieta di un utente nel database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        dieta_json = json.dumps(dieta_dict)
        cursor.execute("""
            UPDATE users
            SET dieta = ?
            WHERE username = ?
        """, (dieta_json, username))
        conn.commit()
    except Exception as e:
        print(f"Errore durante la registrazione della dieta: {e}")
    finally:
        conn.close()
        return True
    
def save_food_list(username, food_list):
    """
    Registra o aggiorna la lista degli alimenti di un utente nel database.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        food_list_json = json.dumps(food_list)
        cursor.execute("""
            UPDATE users
            SET lista_alimenti = ?
            WHERE username = ?
        """, (food_list_json, username))
        conn.commit()
    except Exception as e:
        print(f"Errore durante la registrazione della dieta: {e}")
    finally:
        conn.close()
        return True


def authenticate_user(username, password):
    """
    Verifica se l'username e la password forniti sono validi.
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        if result is None:
            return False  # Username non trovato

        stored_password_hash = result[0]
        return stauth.Hasher.check_pw(password, stored_password_hash)
    except Exception as e:
        print(f"Errore durante l'autenticazione: {e}")
        return False
    finally:
        conn.close()

def register_user(username, first_name, last_name, email, password):
    """
    Registra un nuovo utente nel database.
    """
    if not password:
        raise ValueError("❌ La password non può essere vuota.")
    if len(password) <= 7:
        raise ValueError("❌ La password deve essere di almeno 8 caratteri.")
    password_hash = stauth.Hasher().hash(password)
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email, first_name, last_name, dieta) VALUES (?, ?, ?, ?, ?, ?)",
            (username, password_hash, email, first_name, last_name, None)
        )
        conn.commit()
        st.success("✅ Utente registrato con successo!")
    except sqlite3.IntegrityError:
        st.error("❌ Username già esistente.")
    finally:
        conn.close()

def save_spesa(username, data, spesa):
    conn = sqlite3.connect('dieta.db')
    c = conn.cursor()

    try:
        # Controlla se l'utente esiste già
        c.execute("INSERT INTO storico_spesa (username, data, lista_spesa) VALUES (?, ?, ?)", 
                  (username, data, json.dumps(spesa)))        

        conn.commit()
    except sqlite3.IntegrityError:
        print(f"⚠️ Errore: impossibile inserire la lista della spesa per {username}")
        return False
    finally:
        conn.close()
        return True