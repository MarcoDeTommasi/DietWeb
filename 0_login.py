import streamlit as st
import streamlit_authenticator as stauth
from utils_db import get_users,register_user

if __name__ == "__main__":
    st.set_page_config(layout="wide")

    # Recupera utenti dal database
    config = {"credentials": get_users()}  
    print(config)
    # Converte tutti gli username salvati in lowercase per sicurezza
    config["credentials"]["usernames"] = {k.lower(): v for k, v in config["credentials"]["usernames"].items()}

    # Configura l'autenticazione
    authenticator = stauth.Authenticate(
        config['credentials'],
        "streamlit_auth",
        "random_signature_key",
        30
    )

    # Effettua il login
    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state.get("username"):
        st.session_state["username"] = st.session_state["username"].lower() 

    if st.session_state["authentication_status"]:
        st.title(f'Benvenuto, {config["credentials"]["usernames"][st.session_state["username"]]["first_name"]}!')
        st.toast("Reindirizzamento alla dashboard...")

        st.session_state['nome'] = config["credentials"]["usernames"][st.session_state["username"]]['first_name']
        st.session_state['cognome'] = config["credentials"]["usernames"][st.session_state["username"]]['last_name']
        st.session_state['authenticator'] = authenticator
        st.switch_page("pages/1_home.py")

    elif st.session_state["authentication_status"] is False:
        st.error('❌ Username o password errati.')
    elif st.session_state["authentication_status"] is None:
        st.warning('⚠️ Inserisci username e password.')

    # Form di registrazione
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
            else:
                register_user(new_username, new_name, new_surname, new_email, new_password)
                st.session_state["show_register_form"] = False  # Nasconde il form dopo la registrazione
                st.rerun()
