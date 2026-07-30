from __future__ import annotations

import streamlit as st


def require_authentication() -> bool:
    if st.session_state.get("authentication_status") is True and st.session_state.get(
        "username"
    ):
        return True
    st.warning("Sessione non valida. Effettua nuovamente il login.")
    if st.button("Vai al login"):
        st.switch_page("app.py")
    return False


def render_sidebar(current_page: str) -> None:
    st.session_state["pagina_corrente"] = current_page
    if not require_authentication():
        return
    with st.sidebar:
        first_name = st.session_state.get("nome")
        last_name = st.session_state.get("cognome")
        if first_name or last_name:
            st.subheader(f"Ciao, {' '.join(filter(None, [first_name, last_name]))}!")
        st.caption(f"@{st.session_state['username']}")
        st.caption(f"Pagina: {current_page}")
        st.divider()
        if st.button("Logout 🚪", width="stretch"):
            st.session_state.clear()
            st.switch_page("app.py")
