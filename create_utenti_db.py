import sqlite3
import json
from utils_dicts import dict_lunch_default

def init_db():
    try:
        conn = sqlite3.connect('dieta.db')
        c = conn.cursor()

        # Tabella utenti
        c.execute('''
            CREATE TABLE IF NOT EXISTS utenti (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cognome TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                dieta TEXT
            )
        ''')

        # Converte il dizionario in JSON
        try:
            dieta_json = json.dumps(dict_lunch_default)
        except TypeError as e:
            print(f"❌ Errore nella conversione del JSON: {e}")
            return

        # Controlla se l'utente esiste prima di inserirlo
        c.execute("SELECT COUNT(*) FROM utenti WHERE username = ?", ('marcodefault',))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO utenti (nome, cognome, username, dieta) VALUES (?, ?, ?, ?)", 
                      ('Marco', 'De Tommasi', 'marcodefault', dieta_json))

        # Tabella storico della spesa
        c.execute('''
            CREATE TABLE IF NOT EXISTS storico_spesa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                data TEXT NOT NULL,
                lista_spesa TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES utenti(username)
            )
        ''')

        # Tabella utenti per login
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                password TEXT
            )
        ''')

        conn.commit()
        print("✅ Database inizializzato con successo!")

    except sqlite3.Error as e:
        print(f"❌ Errore durante l'inizializzazione del database: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
