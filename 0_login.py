import os
import sys
from pathlib import Path
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import time

#--client.showSidebarNavigation=False



if __name__ == "__main__":

    # Set page centered
    st.set_page_config(layout="wide")
    
    # Title

    with open('./config/authentication.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # Pre-hashing all plain text passwords once
    # stauth.Hasher.hash_passwords(config['credentials'])
    authentication_status = None
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    

    try:
        authenticator.login()
    except Exception as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        st.title('Logged In')
        st.toast("Taking you to the application...")
        time.sleep(1)
        st.switch_page("pages/1_home.py")
        
        

    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')



