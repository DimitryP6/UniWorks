import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write('### Job Poster Home')
st.write('')
st.write('#### What would you like to do today?')
 
col1, col2, col3 = st.columns(3)
 
with col1:
    if st.button('Manage Job Posts',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/11_Manage_Job_Posts.py')
 
with col2:
    if st.button('View Applications',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/12_View_Applicants.py')
 
with col3:
    if st.button('Job Limitations',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/13_Job_Limits.py')