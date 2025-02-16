import streamlit as st
import sqlite3
from datetime import datetime
from utils_dicts import giorni_map
from utils import get_food_emoji
from utils_db import get_user,register_user,get_user_spesa
import json
from sidebar import mostra_sidebar

def suggerisci_pasto(dict_lunch):
    ora_corrente = datetime.now().hour
    giorno_corrente = datetime.now().strftime("%A")  # Ottiene il giorno in inglese
    giorno_italiano = giorni_map[giorno_corrente]

    # Determina il tipo di pasto in base all'ora
    if ora_corrente < 10:
        pasto_corrente = "Colazione"
    elif 10 <= ora_corrente < 12:
        pasto_corrente = "SpuntinoMattina"
    elif 12 <= ora_corrente < 15:
        pasto_corrente = "Pranzo"
    elif 15 <= ora_corrente < 18:
        pasto_corrente = "SpuntinoPomeriggio"
    else:
        pasto_corrente = "Cena"

    # Trova i suggerimenti per il giorno corrente e il pasto
    pasti_del_giorno = dict_lunch.get(giorno_italiano, {})
    cibi_suggeriti = pasti_del_giorno.get(pasto_corrente, {})

    # Costruisci il messaggio con emoji
    if cibi_suggeriti:
        messaggio = f"Prossimo pasto {pasto_corrente.replace('_', ' ').capitalize()}:\n"
        for alimento, info in cibi_suggeriti.items():
            emoji = get_food_emoji(alimento)
            quantity = info['Quantità']
            unit = info['Unità']
            messaggio += f"- {emoji} {alimento.replace('_', ' ')} : {quantity} {unit}\n"
    else:
        messaggio = "Non ci sono suggerimenti disponibili per il tuo pasto attuale."

    return messaggio

st.set_page_config(layout="wide")
st.session_state['pagina_corrente']="home"
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
        col1,col2 = st.columns(2)
        with col1:
            st.divider()
            st.subheader("1. 🛒 Genera la lista della spesa per la settimana!")
            if st.button("Vai al Generatore"):
                st.switch_page('pages/3_lista_spesa.py')

            st.divider()
            st.subheader("2. 📊 Guarda le analitiche di Acquisto!")
            if st.button("Vai alle Analitiche"):
                if len(get_user_spesa(username))>1:
                    st.switch_page('pages/4_analytics.py')
                else:
                    st.error("❌ Sezione Accessibile con almeno 2 spese effettuate e salvate!")
            st.divider()
            st.subheader("3. ✏️  Modifica la tua dieta esistente")
            if st.button("Modifica Dieta"):
                st.session_state["review_complete"] = False
                st.session_state["current_day"] = 0
                st.switch_page('pages/2_upload_diet.py')
        with col2:
            st.write("## 🍽️ Suggerimento per il prossimo pasto")
            st.write(f"### {suggerisci_pasto(dieta)}")

    else:
        # Username non trovato → Chiede Nome e Cognome
        st.warning("⚠️ Username non trovato! Inserisci Nome e Cognome per registrarti.")

        # Recupera Nome e Cognome dalla sessione per non perderli al refresh
        if "nome" not in st.session_state:
            st.session_state["nome"] = None
        if "cognome" not in st.session_state:
            st.session_state["cognome"] = None
        mostra_sidebar()
        nome = st.text_input("Nome:", value=st.session_state["nome"], key="input_nome")
        cognome = st.text_input("Cognome:", value=st.session_state["cognome"], key="input_cognome")

        # Aggiorna i valori in sessione mentre vengono digitati
        if nome and cognome and username:
            if st.button("📤 Registra e Carica il tuo Piano Nutrizionale"):
                register_user(nome, cognome, username)
                st.switch_page("pages/2_upload_diet.py")
        else:
            st.info("➡️ Inserisci Nome e Cognome per continuare.")

else:
    st.warning("⚠️ Devi inserire il tuo username per accedere.")
