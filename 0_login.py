import os
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time
import hashlib

CONFIG_PATH = './config/authentication.yaml'

def save_config(config):
    """Salva il file YAML aggiornato."""
    with open(CONFIG_PATH, 'w') as file:
        yaml.dump(config, file,default_flow_style=False, sort_keys=False)

if __name__ == "__main__":
    st.set_page_config(layout="wide")

    # Carica il file di configurazione
    with open(CONFIG_PATH) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
         config['cookie']['name'],
         config['cookie']['key'],
         config['cookie']['expiry_days']
    )

    # Effettua il login
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        st.title('Benvenuto!')
        st.toast("Reindirizzamento alla dashboard...")
        print(st.session_state['username'])
        st.session_state['nome'] = config["credentials"]["usernames"][st.session_state['username']]['first_name']
        st.session_state['cognome'] = config["credentials"]["usernames"][st.session_state['username']]['last_name']
        st.session_state['authenticator'] = authenticator
        st.switch_page("pages/1_home.py")

    elif st.session_state["authentication_status"] is False:
        st.error('❌ Username o password errati.')
    elif st.session_state["authentication_status"] is None:
        st.warning('⚠️ Inserisci username e password.')


    
    if "show_register_form" not in st.session_state:
        st.session_state["show_register_form"] = False

    if st.button("📝 Nuovo utente? Registrati qui"):
        st.session_state["show_register_form"] = True

    if st.session_state["show_register_form"]:
        with st.form("register_form"):
            new_name = st.text_input("Nome")
            new_surname = st.text_input("Cognome")
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Conferma Password", type="password")
            submit_button = st.form_submit_button("Registrati")

        if submit_button:
            if new_password != confirm_password:
                st.error("❌ Le password non corrispondono!")
            elif new_username in config["credentials"]["usernames"]:
                st.error("⚠️ Username già esistente!")
            else:
                hashed_password = stauth.Hasher(new_password).hash(password=new_password)
                config["credentials"]["usernames"][new_username] = {
                    "email": new_email,
                    "failed_login_attempts": 0,
                    "first_name": new_name,
                    "last_name": new_surname,
                    "logged_in": False,
                    "password": hashed_password
                }
                save_config(config)
                st.success("✅ Registrazione completata! Ora puoi effettuare il login.")
                st.session_state["show_register_form"] = False  # Nasconde il form dopo la registrazione
                st.rerun()


