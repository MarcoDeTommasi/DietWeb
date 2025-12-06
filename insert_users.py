import sqlite3
import json
from utils_dicts import dict_lunch_default
from dieta_marco_temp import dieta_temp
def inserisci_utenti():
    try:
        conn = sqlite3.connect('dieta.db')
        c = conn.cursor()

        # Converte i dizionari in JSON
        try:
            dieta_marco_json = json.dumps(dieta_temp)
            dieta_nicola_json = json.dumps(dieta_temp)
            dieta_ribbi_json = json.dumps(dieta_temp)
        except TypeError as e:
            print(f"❌ Errore nella conversione del JSON: {e}")
            return

        # Inserimento utente Marco se non esiste già
        c.execute("SELECT COUNT(*) FROM utenti WHERE username = ?", ('marcodefault',))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO utenti (nome, cognome, username, dieta) VALUES (?, ?, ?, ?)", 
                      ('Marco', 'De Tommasi', 'marcodefault', dieta_marco_json))
            print("✅ Utente 'marcodefault' inserito con successo.")

        # Inserimento utente Nicola se non esiste già
        c.execute("SELECT COUNT(*) FROM utenti WHERE username = ?", ('nicoladefault',))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO utenti (nome, cognome, username, dieta) VALUES (?, ?, ?, ?)", 
                      ('Nicola', 'De Tommasi', 'nicoladefault', dieta_nicola_json))
            print("✅ Utente 'nicoladefault' inserito con successo.")
        c.execute("SELECT COUNT(*) FROM utenti WHERE username = ?", ('robertadefault',))
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO utenti (nome, cognome, username, dieta) VALUES (?, ?, ?, ?)", 
                      ('Roberta', 'De Tommasi', 'robertadefault', dieta_ribbi_json))
            print("✅ Utente 'robertadefault' inserito con successo.")

        conn.commit()
        print("✅ Operazione completata con successo!")

    except sqlite3.Error as e:
        print(f"❌ Errore durante l'inserimento degli utenti: {e}")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    inserisci_utenti()
