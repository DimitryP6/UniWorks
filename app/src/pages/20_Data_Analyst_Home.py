import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title(f"Welcome, {st.session_state['first_name']}!")
st.write('### Data Analyst Home')
st.write('')
st.write('#### What would you like to do today?')
 
col1, col2, col3 = st.columns(3)
 
with col1:
    if st.button('Analytics Dashboard',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/21_Analytics_Dashboard.py')
 
with col2:
    if st.button('Application Trends',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/22_Application_Trends.py')
 
with col3:
    if st.button('Data Reports',
                 type='primary',
                 use_container_width=True):
        st.switch_page('pages/23_Data_Reports.py')