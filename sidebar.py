import streamlit as st

def mostra_sidebar():
    if 'username' not in st.session_state:
        st.session_state.username = None
        st.session_state.nome = None
        st.session_state.cognome = None
        st.session_state.pagina_corrente = 'home'

    with st.sidebar:
        if st.session_state.nome is not None and st.session_state.cognome is not None:
            st.write(f"### Ciao, {st.session_state.nome} {st.session_state.cognome}! ")
        st.write(f"Username: {st.session_state.username}")
        st.write(f"Pagina corrente: {st.session_state.pagina_corrente}")

        if st.button("Logout 🚪"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page('pages/1_home.py')
