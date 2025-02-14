import streamlit as st
import sqlite3
import json

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

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

# Homepage Streamlit
st.title("🍽️ DietApp Web Version!")
st.write("Benvenuta/o! Questa applicazione ti aiuterà a gestire la tua dieta e la tua lista della spesa.")

st.subheader("🔹 Inserisci il tuo username per accedere")
username = st.text_input("Username (univoco):", key="input_username")

if username:
    nome_db, cognome_db, dieta = get_user(username)

    if nome_db:
        # Utente trovato → Salvo i dati nella sessione
        st.session_state['username'] = username
        st.session_state['nome'] = nome_db
        st.session_state['cognome'] = cognome_db
        st.session_state['dict_lunch'] = dieta

        st.success(f"🎉 Bentornato {nome_db} {cognome_db}!")

        st.divider()
        st.subheader("1. 🛒 Genera la lista della spesa per la settimana!")
        if st.button("Vai al Generatore"):
            st.switch_page('pages/3_lista_spesa.py')

        st.divider()
        st.subheader("2. 📊 Guarda le analitiche di consumo!")
        if st.button("Vai alle Analitiche"):
            st.switch_page('pages/4_analisi_consumo.py')

    else:
        # Username non trovato → Chiede Nome e Cognome
        st.warning("⚠️ Username non trovato! Inserisci Nome e Cognome per registrarti.")

        # Recupera Nome e Cognome dalla sessione per non perderli al refresh
        if "nome" not in st.session_state:
            st.session_state["nome"] = ""
        if "cognome" not in st.session_state:
            st.session_state["cognome"] = ""

        nome = st.text_input("Nome:", value=st.session_state["nome"], key="input_nome")
        cognome = st.text_input("Cognome:", value=st.session_state["cognome"], key="input_cognome")

        # Aggiorna i valori in sessione mentre vengono digitati
        st.session_state["nome"] = nome
        st.session_state["cognome"] = cognome

        if nome and cognome:
            if st.button("📤 Registra e Carica il tuo Piano Nutrizionale"):
                register_user(nome, cognome, username)
                st.switch_page("pages/2_upload_diet.py")
        else:
            st.info("➡️ Inserisci Nome e Cognome per continuare.")

else:
    st.warning("⚠️ Devi inserire il tuo username per accedere.")
