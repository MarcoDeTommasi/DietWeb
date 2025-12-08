import streamlit as st
import streamlit_authenticator as stauth
from utils_db import authenticate_user, register_user, initialize_sqlite_db

def main():
    st.set_page_config(layout="wide")

    # Inizializza il database SQLite

    # Configura l'autenticazione
    authenticator = stauth.Authenticate(
        {"usernames": {}},  # Configurazione vuota, verrà gestita dinamicamente
        "streamlit_auth",
        "random_signature_key",
        30
    )

    # Effettua il login
    with st.form("login_form"):
        st.subheader("Effettua il login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

    if login_button:
        if authenticate_user(username, password):
            st.success(f"Benvenuto, {username}!")
            st.toast("Reindirizzamento alla dashboard...")
            st.session_state["username"] = username
            st.session_state["authenticator"] = authenticator
            st.session_state["authentication_status"] = True
            st.switch_page("pages/1_home.py")
        else:
            st.error("❌ Username o password errati.")

    # Mostra il modulo di registrazione
    show_registration_form()

def show_registration_form():
    """
    Mostra il modulo di registrazione per nuovi utenti.
    """
    if "show_register_form" not in st.session_state:
        st.session_state["show_register_form"] = False

    if st.button("📝 Nuovo utente? Registrati qui"):
        st.session_state["show_register_form"] = True

    if st.session_state["show_register_form"]:
        st.subheader("Modulo di Registrazione")
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
            elif not new_username or not new_password:
                st.error("❌ Tutti i campi sono obbligatori!")
            else:
                register_user(new_username, new_name, new_surname, new_email, new_password)
                st.success("✅ Registrazione completata con successo!")
                st.session_state["show_register_form"] = False  # Nasconde il form dopo la registrazione
                st.rerun()

if __name__ == "__main__":
    main()