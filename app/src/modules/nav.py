# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/40_About.py", label="About", icon="🧠")


# ---- Role: job_seeker (Sarah) -----------------------------------------------
 
def job_seeker_home_nav():
    st.sidebar.page_link(
        "pages/42_Job_Seeker_Home.py", label="Job Seeker Home", icon="👤"
    )


def browse_jobs_nav():
    st.sidebar.page_link(
        "pages/41_Browse_Jobs.py", label="Browse Jobs", icon="🔍"
    )


def my_applications_nav():
    st.sidebar.page_link(
        "pages/43_My_Applications.py", label="My Applications", icon="📋"
    )


def my_profile_nav():
    st.sidebar.page_link(
        "pages/44_My_Profile.py", label="My Profile", icon="📝"
    )

# ---- Role: job_poster (Tom) -------------------------------------------------
 
def job_poster_home_nav():
    st.sidebar.page_link(
        "pages/10_Job_Poster_Home.py", label="Job Poster Home", icon="🏢"
    )
 
 
def manage_posts_nav():
    st.sidebar.page_link(
        "pages/11_Manage_Job_Posts.py", label="Manage Job Posts", icon="📌"
    )
 
 
def view_applicants_nav():
    st.sidebar.page_link(
        "pages/12_View_Applicants.py", label="View Applicants", icon="👥"
    )
 
 
def post_limits_nav():
    st.sidebar.page_link(
        "pages/13_Job_Limits.py", label="Job Limits & Links", icon="⚙️"
    )


 
# ---- Role: data_analyst (Lauren) --------------------------------------------
 
def data_analyst_home_nav():
    st.sidebar.page_link(
        "pages/20_Data_Analyst_Home.py", label="Data Analyst Home", icon="📊"
    )
 
 
def analytics_dashboard_nav():
    st.sidebar.page_link(
        "pages/21_Analytics_Dashboard.py", label="Analytics Dashboard", icon="📈"
    )
 
 
def application_trends_nav():
    st.sidebar.page_link(
        "pages/22_Application_Trends.py", label="Application Trends", icon="📉"
    )
 
 
def data_reports_nav():
    st.sidebar.page_link(
        "pages/23_Data_Reports.py", label="Data Reports", icon="📑"
    )
 
 
# ---- Role: administrator (Alex) ---------------------------------------------
 
def admin_home_nav():
    st.sidebar.page_link(
        "pages/30_Admin_Home.py", label="Admin Home", icon="🖥️"
    )
 
 
def user_management_nav():
    st.sidebar.page_link(
        "pages/31_User_Management.py", label="User Management", icon="👨‍💻"
    )
 
 
def system_logs_nav():
    st.sidebar.page_link(
        "pages/32_System_Logs.py", label="System Logs", icon="📜"
    )
 
 
def admin_reports_nav():
    st.sidebar.page_link(
        "pages/33_Admin_Reports.py", label="Admin Reports", icon="🗂️"
    )


# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "pol_strat_advisor":
            pol_strat_home_nav()
            world_bank_viz_nav()
            map_demo_nav()

        if st.session_state["role"] == "usaid_worker":
            usaid_worker_home_nav()
            ngo_directory_nav()
            add_ngo_nav()
            prediction_nav()
            api_test_nav()
            classification_nav()

        if st.session_state["role"] == "job_seeker":
            job_seeker_home_nav()
            browse_jobs_nav()
            my_applications_nav()
            my_profile_nav()

 
        if st.session_state["role"] == "job_poster":
            job_poster_home_nav()
            manage_posts_nav()
            view_applicants_nav()
            post_limits_nav()
 
        if st.session_state["role"] == "data_analyst":
            data_analyst_home_nav()
            analytics_dashboard_nav()
            application_trends_nav()
            data_reports_nav()
 
        if st.session_state["role"] == "administrator":
            admin_home_nav()
            user_management_nav()
            system_logs_nav()
            admin_reports_nav()

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
