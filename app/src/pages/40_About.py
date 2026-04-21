import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About this App")

st.markdown(
    """
    **UniWorks** is a data-driven internship and job search platform designed for 
    university students, employers, career analysts, and system administrator in 
    one centralized system
    """
)

# Add a button to return to home page
if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
