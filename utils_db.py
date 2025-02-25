import sqlite3
import streamlit as st
import json
import pandas as pd
import streamlit_authenticator as stauth

# Funzione per verificare se un utente esiste nel database
def get_user(username):
    conn = sqlite3.connect('dieta.db')
    c = conn.cursor()
    c.execute("SELECT nome, cognome, dieta FROM utenti WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if result:
        nome, cognome, dieta_json = result
        dieta = json.loads(dieta_json) if dieta_json else {}
        return nome, cognome, dieta
    return None, None, None

# Funzione per registrare un nuovo utente
def register_user(nome, cognome, username):
    conn = sqlite3.connect('dieta.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO utenti (nome, cognome, username, dieta) VALUES (?, ?, ?, ?)", 
                  (nome, cognome, username, json.dumps({})))  # Inizializza con dieta vuota
        conn.commit()
        st.success(f"🎉 Benvenuto {nome} {cognome}! Ora puoi caricare il tuo piano nutrizionale.")
        st.session_state["username"] = username
        st.session_state["nome"] = nome
        st.session_state["cognome"] = cognome
    except sqlite3.IntegrityError:
        st.error("⚠️ Questo username è già in uso. Scegline un altro.")
    conn.close()


def save_diet(username, dieta):
    conn = sqlite3.connect('dieta.db')
    c = conn.cursor()

    try:
        # Controlla se l'utente esiste già
        c.execute("SELECT * FROM utenti WHERE username = ?", (username,))
        user = c.fetchone()
        
        if user:
            # Se l'utente esiste, aggiorna la dieta
            c.execute("UPDATE utenti SET dieta = ? WHERE username = ?", (json.dumps(dieta), username))
        else:
            st.error("⚠️ Errore: impossibile salvare la dieta per l'username {username}")
            return False

        conn.commit()
    except sqlite3.IntegrityError:
        print(f"⚠️ Errore: trovare utente con username {username}")
        return False
    finally:
        conn.close()
        return True


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


def get_user_spesa(username):
    """
    Recupera tutte le diete salvate per un dato username e le restituisce in un DataFrame.
    """
    conn = sqlite3.connect('dieta.db')
    c = conn.cursor()
    
    try:
        # Recupera tutte le diete per l'utente specificato
        c.execute("SELECT data, lista_spesa FROM storico_spesa WHERE username = ?", (username,))
        rows = c.fetchall()
        
        # Controlla se ci sono risultati
        if not rows:
            print(f"⚠️ Nessuna dieta trovata per l'utente {username}.")
            return pd.DataFrame(columns=["Data", "Lista Spesa"])
        
        # Converte i risultati in un DataFrame
        df = pd.DataFrame(rows, columns=["Data", "Lista Spesa"])
        
        # Decodifica la colonna "Lista Spesa" da JSON a dizionario
        df["Lista Spesa"] = df["Lista Spesa"].apply(lambda x: json.loads(x))
        
        return df
    
    except Exception as e:
        print(f"❌ Errore durante il recupero delle diete: {e}")
        return pd.DataFrame(columns=["Data", "Lista Spesa"])
    
    finally:
        conn.close()

def register_user(username, first_name, last_name, email, password):
    conn = sqlite3.connect("dieta.db")
    cursor = conn.cursor()
    
    username = username.lower()  # 🔹 Converte in lowercase

    hashed_password = stauth.Hasher([password]).generate()[0]

    try:
        cursor.execute("INSERT INTO users (username, first_name, last_name, email, password) VALUES (?, ?, ?, ?, ?)", 
                       (username, first_name, last_name, email, hashed_password))
        conn.commit()
        st.success("✅ Registrazione completata! Ora puoi effettuare il login.")
    except sqlite3.IntegrityError:
        st.error("⚠️ Username già esistente!")
    finally:
        conn.close()

def get_users():
    conn = sqlite3.connect("dieta.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, first_name, last_name, email, password FROM users")
    users = cursor.fetchall()
    conn.close()
    
    credentials = {"usernames": {}}
    for user in users:
        username, first_name, last_name, email, password = user
        credentials["usernames"][username] = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password  # La password è già hashata
        }
    return credentials
# Esempio di utilizzo
# df_diete = get_user_diets("test_user")
# print(df_diete)
