import sqlite3
import json
from utils_dicts import dict_lunch_default

import sqlite3

def init_db():
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

    dieta_json = json.dumps(dict_lunch_default)
    # Inserisci i dati di esempio
    c.execute("INSERT OR IGNORE INTO utenti (nome, cognome, username, dieta) VALUES (?, ? ,? ,?)", ('Marco','De Tommasi','MarcoDefault', dieta_json))

    
    # Tabella storico delle liste della spesa
    c.execute('''
        CREATE TABLE IF NOT EXISTS storico_spesa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            data TEXT NOT NULL,
            lista_spesa TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES utenti(username)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database inizializzato con successo!")

if __name__ == "__main__":
    init_db()
