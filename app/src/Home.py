##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")
st.title('CS 3200 Project Template')
st.write('#### Hi! As which user would you like to log in?')

# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

# Job Seeker - Sarah Smith
if st.button("Act as Sarah, a Job Seeker",
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'job_seeker'
    st.session_state['first_name'] = 'Sarah'
    logger.info("Logging in as Job Seeker Persona")
    st.switch_page('pages/00_Job_Seeker_Home.py')
 
# Job Poster - Tom Bombadil
if st.button('Act as Tom, a Job Poster',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'job_poster'
    st.session_state['first_name'] = 'Tom'
    logger.info("Logging in as Job Poster Persona")
    st.switch_page('pages/10_Job_Poster_Home.py')
 
# Data Analyst - Lauren Mitchell
if st.button('Act as Lauren, a Data Analyst',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'data_analyst'
    st.session_state['first_name'] = 'Lauren'
    logger.info("Logging in as Data Analyst Persona")
    st.switch_page('pages/20_Data_Analyst_Home.py')
 
# System Administrator - Alex Rial
if st.button('Act as Alex, a System Administrator',
             type='primary',
             use_container_width=True):
    st.session_state['authenticated'] = True
    st.session_state['role'] = 'administrator'
    st.session_state['first_name'] = 'Alex'
    logger.info("Logging in as System Administrator Persona")
    st.switch_page('pages/30_Admin_Home.py')