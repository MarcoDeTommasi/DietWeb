import streamlit as st
from datetime import datetime
from utils_dicts import giorni_map
from utils import get_food_emoji
from utils_db import get_user_diet,get_user_name,get_user_spesa,update_password,get_user_food_list
from sidebar import mostra_sidebar
from datetime import datetime
from home import determina_pasto_corrente, suggerisci_pasti

st.set_page_config(layout="wide")

def home():

    username = st.session_state['username']
    st.session_state['pagina_corrente']= "home"
    st.session_state['nome'], st.session_state['cognome'] = get_user_name(username)
    nome = st.session_state['nome']
    cognome = st.session_state['cognome']
    dieta = get_user_diet(username)
    food_list = get_user_food_list(username)
    if food_list is not None:
        st.session_state['food_list'] = food_list
    # Recupera Nome e Cognome dalla sessione per non perderli al refresh
    mostra_sidebar()

    st.title("🍽️ DietApp Web Version!")
    st.write(f"Benvenuta/o {st.session_state['nome']}!")
    st.write("Questa applicazione ti aiuterà a gestire la tua dieta e la tua lista della spesa.")

    if "show_password_form" not in st.session_state:
        st.session_state["show_password_form"] = False

    # Bottone per mostrare il form di cambio password
    if st.button("🔒 Cambia Password"):
        st.session_state["show_password_form"] = True

    # Mostra il form solo se richiesto
    if st.session_state["show_password_form"]:
        with st.form("cambia_password_form"):
            if st.session_state["authentication_status"]:
                username = st.session_state["username"]  # Recupera l'utente loggato
                
                new_password = st.text_input("Nuova Password", type="password")
                confirm_password = st.text_input("Conferma Password", type="password")
                submit_button = st.form_submit_button("Cambia Password")

            if submit_button:
                if new_password == confirm_password:
                    # Hash della nuova password
                    update_password(username, new_password)  # 🔄 Salva nel DB
                    st.success("✅ Password modificata con successo!")
                    st.session_state["show_password_form"] = False
                    st.rerun()  # Chiude il form dopo la modifica
                else:
                    st.error("❌ Le password non corrispondono!")

    if dieta is not None and food_list is not None:
        st.session_state['dict_lunch'] = dieta
        st.success(f"🎉 Dieta recuperata correttamente!")
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
                st.session_state['food_list'] = food_list
                st.switch_page('pages/2_upload_diet.py')
        with col2:
            st.write("## 🍽️ Suggerimento per il prossimo pasto")
            giorno_corrente = giorni_map[datetime.now().strftime("%A")]
            giorno_selezionato = st.selectbox("Seleziona un giorno:", list(giorni_map.values()), index=list(giorni_map.values()).index(giorno_corrente))

            pasto_corrente = determina_pasto_corrente()
            pasti_disponibili = ["Colazione", "Pranzo", "Cena"]
            pasti_selezionati = st.multiselect("Seleziona i pasti da visualizzare:", pasti_disponibili, default=[pasto_corrente])
            
            col1, col2 = st.columns(2)
            pasti_principali, spuntini = suggerisci_pasti(dieta, giorno_selezionato, pasti_selezionati, food_list, include_spuntini=True)
            
            with col1:
                st.write("## 🍽️ Pasti Principali")
                st.write(pasti_principali)
            with col2:
                st.write("## 🥪 Spuntini")
                st.write(spuntini)
    else:
        # Username non trovato → Chiede Nome e Cognome
        st.warning(f"⚠️ Dieta non ancora inserita per {nome} {cognome} (username: {username}).")

        # Aggiorna i valori in sessione mentre vengono digitati
        if nome and cognome and username:
            if st.button("📤 Registra e Carica il tuo Piano Nutrizionale"):
                st.switch_page("pages/2_upload_diet.py")
        else:
            st.info("➡️ Inserisci Nome e Cognome per continuare.")


if __name__ == "__main__":
    if "authentication_status" in st.session_state.keys() and st.session_state["authentication_status"]:
        home()
    else:
        st.error("❌ Not Authenticated! ")