from __future__ import annotations

import logging

import streamlit as st

from dietapp.database import init_database, session_scope
from dietapp.repositories import (
    RepositoryError,
    authenticate_user,
    get_user,
    register_user,
)
from dietapp.security import (
    normalise_username,
    validate_password,
    validate_username,
)


LOGGER = logging.getLogger(__name__)


@st.cache_resource
def _initialise() -> bool:
    try:
        init_database()
        return True
    except Exception:
        LOGGER.exception("Database initialisation failed")
        st.error(
            "Impossibile collegarsi al database. Controlla DATABASE_URL e riprova."
        )
        return False


def _login_form() -> None:
    with st.form("login_form"):
        st.subheader("Accedi")
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input(
            "Password", type="password", autocomplete="current-password"
        )
        submitted = st.form_submit_button(
            "Accedi", type="primary", width="stretch"
        )

    if not submitted:
        return
    if not username.strip() or not password:
        st.error("Inserisci username e password.")
        return
    try:
        with session_scope() as db:
            authenticated = authenticate_user(db, username, password)
            user = get_user(db, username) if authenticated else None
        if not authenticated or user is None:
            st.error("Username o password non corretti.")
            return
        st.session_state.clear()
        st.session_state.update(
            {
                "username": user.username,
                "nome": user.first_name,
                "cognome": user.last_name,
                "authentication_status": True,
            }
        )
        st.switch_page("pages/1_home.py")
    except RepositoryError:
        LOGGER.exception("Login database operation failed")
        st.error("Login temporaneamente non disponibile. Riprova tra poco.")


def _registration_form() -> None:
    with st.expander("Non hai un account? Registrati"):
        with st.form("registration_form", clear_on_submit=False):
            first_name = st.text_input("Nome")
            last_name = st.text_input("Cognome")
            email = st.text_input("Email", autocomplete="email")
            username = st.text_input("Scegli uno username", autocomplete="username")
            password = st.text_input(
                "Scegli una password", type="password", autocomplete="new-password"
            )
            confirmation = st.text_input(
                "Conferma la password",
                type="password",
                autocomplete="new-password",
            )
            submitted = st.form_submit_button(
                "Crea account", width="stretch"
            )

        if not submitted:
            return
        username = normalise_username(username)
        username_error = validate_username(username)
        password_error = validate_password(password)
        if not first_name.strip() or not last_name.strip():
            st.error("Nome e cognome sono obbligatori.")
        elif "@" not in email or len(email) > 254:
            st.error("Inserisci un indirizzo email valido.")
        elif username_error:
            st.error(username_error)
        elif password_error:
            st.error(password_error)
        elif password != confirmation:
            st.error("Le password non corrispondono.")
        else:
            try:
                with session_scope() as db:
                    created = register_user(
                        db,
                        username,
                        first_name,
                        last_name,
                        email,
                        password,
                    )
                if created:
                    st.success("Account creato. Ora puoi effettuare il login.")
                else:
                    st.error("Username o email già in uso.")
            except RepositoryError:
                LOGGER.exception("Registration database operation failed")
                st.error("Registrazione temporaneamente non disponibile.")


def main() -> None:
    st.set_page_config(
        page_title="DietApp",
        page_icon="🍽️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.title("🍽️ DietApp")
    st.caption("Piano alimentare, dispensa e lista della spesa in un unico posto.")
    if not _initialise():
        st.stop()
    if st.session_state.get("authentication_status"):
        st.success(f"Sei già autenticato come {st.session_state.get('username')}.")
        if st.button("Vai alla dashboard", type="primary"):
            st.switch_page("pages/1_home.py")
        return
    _login_form()
    _registration_form()


if __name__ == "__main__":
    main()
