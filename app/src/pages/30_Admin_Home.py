import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome System Administrator, {st.session_state['first_name']}.")
st.write('### What would you like to do today?')

if st.button('Manage Users',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/31_User_Management.py')

if st.button('View System Logs',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/32_System_Logs.py')

if st.button('Clean Up Data',
             type='primary',
             use_container_width=True):
    st.switch_page('pages/33_Admin_Reports.py')