import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write('### Job Seeker Home')
st.write('')
st.write('#### What would you like to do today?')

col1, col2, col3 = st.columns(3)

with col1:
    if st.button('Browse Jobs',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/41_Browse_Jobs.py')

with col2:
    if st.button('My Applications',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/43_My_Applications.py')

with col3:
    if st.button('My Profile',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/44_My_Profile.py')
