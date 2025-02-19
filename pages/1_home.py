import streamlit as st
import sqlite3
from datetime import datetime
from utils_dicts import giorni_map
from utils import get_food_emoji
from utils_db import get_user,register_user,get_user_spesa
import json
from sidebar import mostra_sidebar

import streamlit as st
from datetime import datetime

giorni_map = {
    "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì", "Thursday": "Giovedì",
    "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
}

def determina_pasto_corrente():
    ora_corrente = datetime.now().hour
    if ora_corrente < 11:
        return "Colazione"
    elif 11 <= ora_corrente < 16:
        return "Pranzo"
    else:
        return "Cena"

def suggerisci_pasti(dict_lunch, giorno, pasti_selezionati, include_spuntini=False):
    pasti_del_giorno = dict_lunch.get(giorno, {})
    pasti_principali = ""
    spuntini = ""
    
    for pasto, cibi in pasti_del_giorno.items():
        if pasto in ["Colazione", "Pranzo", "Cena"] and pasto in pasti_selezionati:
            pasti_principali += f"### {pasto.replace('_', ' ').capitalize()}\n"
            for alimento, info in cibi.items():
                emoji = get_food_emoji(alimento)
                quantity = info['Quantità']
                unit = info['Unità']
                pasti_principali += f"- {emoji} {alimento.replace('_', ' ')}: {quantity} {unit}\n"
            pasti_principali += "\n"
        elif "Spuntino" in pasto:
            spuntini += f"###  Spuntino {pasto.replace('Spuntino', '').capitalize()}\n"
            for alimento, info in cibi.items():
                emoji = get_food_emoji(alimento)
                quantity = info['Quantità']
                unit = info['Unità']
                spuntini += f"- {emoji} {alimento.replace('_', ' ')}: {quantity} {unit}\n"
            spuntini += "\n"
    
    return pasti_principali, spuntini

def home():
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
            mostra_sidebar()
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
                giorno_corrente = giorni_map[datetime.now().strftime("%A")]
                giorno_selezionato = st.selectbox("Seleziona un giorno:", list(giorni_map.values()), index=list(giorni_map.values()).index(giorno_corrente))

                pasto_corrente = determina_pasto_corrente()
                pasti_disponibili = ["Colazione", "Pranzo", "Cena"]
                pasti_selezionati = st.multiselect("Seleziona i pasti da visualizzare:", pasti_disponibili, default=[pasto_corrente])
                
                col1, col2 = st.columns(2)
                pasti_principali, spuntini = suggerisci_pasti(dieta, giorno_selezionato, pasti_selezionati, include_spuntini=True)
                
                with col1:
                    st.write("## 🍽️ Pasti Principali")
                    st.write(pasti_principali)
                with col2:
                    st.write("## 🥪 Spuntini")
                    st.write(spuntini)
        else:
            # Username non trovato → Chiede Nome e Cognome
            st.warning("⚠️ Username non trovato! Inserisci Nome e Cognome per registrarti.")

            # Recupera Nome e Cognome dalla sessione per non perderli al refresh
            st.session_state["nome"] = None
            st.session_state["cognome"] = None
            mostra_sidebar()
            nome = st.text_input("Nome:", value=st.session_state["nome"], key="input_nome")
            cognome = st.text_input("Cognome:", value=st.session_state["cognome"], key="input_cognome")

            # Aggiorna i valori in sessione mentre vengono digitati
            if nome and cognome and username:
                if st.button("📤 Registra e Carica il tuo Piano Nutrizionale"):
                    for key in st.session_state.keys():
                        if key != "authentication_status":
                            del st.session_state[key]
                    register_user(nome, cognome, username)
                    st.switch_page("pages/2_upload_diet.py")
            else:
                st.info("➡️ Inserisci Nome e Cognome per continuare.")

    else:
        st.warning("⚠️ Devi inserire il tuo username per accedere.")

if __name__ == "__main__":
    if "authentication_status" in st.session_state.keys() and st.session_state["authentication_status"]:
        home()
    else:
        st.error("❌ Not Authenticated! ")