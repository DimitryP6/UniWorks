import logging

logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Job Posts")

if "show_success_modal" not in st.session_state:
    st.session_state.show_success_modal = False
if "success_message" not in st.session_state:
    st.session_state.success_message = ""
if "reset_form" not in st.session_state:
    st.session_state.reset_form = False
if "form_key_counter" not in st.session_state:
    st.session_state.form_key_counter = 0

@st.dialog("Success")
def show_success_dialog(message):
    st.markdown(f"### {message}")
    if st.button("OK", use_container_width=True):
        st.session_state.show_success_modal = False
        st.session_state.success_message = ""
        st.rerun()

# Handle form reset
if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

JOB_DURATION_OPTIONS   = ["4-Month COOP", "6-Month COOP", "8-Month COOP", "Internship"]
ATTENDANCE_OPTIONS     = ["Hybrid", "On-site", "Remote"]
US_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

BASE_URL = "http://web-api:4000/job_poster/job_post"

tab1, tab2, tab3, tab4 = st.tabs(["View Posts", "Create Post", "Update Post", "Delete Post"])


with tab1:
    st.subheader("View Job Posts")
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            posts = response.json()
            if posts:
                st.write(f"Found {len(posts)} posts")
                for post in posts:
                    with st.expander(f"Post #{post['post_id']} — {post.get('job_title', 'N/A')}"):
                        st.write(f"**Duration:** {post.get('job_duration', 'N/A')}")
                        st.write(f"**Salary:** {post.get('job_salary', 'N/A')}")
                        st.write(f"**Location:** {post.get('city_state', 'N/A')}")
                        st.write(f"**Attendance:** {post.get('attendance_type', 'N/A')}")
                        st.write(f"**Active Status:** {post.get('is_active', 'N/A')}")
                        st.write(f"**Poster ID:** {post.get('poster_id', 'N/A')}")
                        try:
                            links_response = requests.get(f"{BASE_URL}/{post['post_id']}/job_links")
                            if links_response.status_code == 200:
                                links = links_response.json()
                                if links:
                                    st.write("**Job Links:**")
                                    for link in links:
                                        st.markdown(f"- [{link['job_link']}]({link['job_link']})")
                                else:
                                    st.write("**Job Links:** None")
                        except requests.exceptions.RequestException:
                            st.write("**Job Links:** Could not fetch")
            else:
                st.info("No job postings found.")
        else:
            st.error(f"Failed to fetch posts: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")


with tab2:
    st.subheader("Create New Job Post")

    with st.form(f"create_post_form_{st.session_state.form_key_counter}"):
        poster_id = st.number_input("Poster ID *", min_value = 1, step = 1)
        job_title = st.text_input("Job Title *", placeholder = "e.g., Software Engineer Intern")
        job_duration = st.selectbox("Job Duration *", JOB_DURATION_OPTIONS)
        attendance = st.selectbox("Attendance Type *", ATTENDANCE_OPTIONS)
        job_salary = st.number_input("Salary (optional)", min_value = 0.0, step = 5.0)
        job_desc = st.text_area("Job Description (optional)")
        job_link = st.text_input("Job Link (optional)", placeholder = "e.g., https://company.com/jobs/123")

        city = st.text_input("City *", placeholder="e.g., Boston")
        state = st.selectbox("State *", US_STATES)

        submitted = st.form_submit_button("Create Post")

        if submitted:
            if not all([poster_id, job_title, city]):
                st.error("Please fill in all required fields marked with *")
            else:
                post_data = {
                    "poster_id" : int(poster_id),
                    "job_title" : job_title,
                    "job_duration" : job_duration,
                    "attendance_type" : attendance,
                    "job_salary" : job_salary if job_salary > 0 else None,
                    "job_description" : job_desc if job_desc else None,
                    "city_state" : f"{city}, {state}",
                    "job_link" : job_link if job_link else None,
                }
                try:
                    response = requests.post(BASE_URL, json = post_data)
                    if response.status_code == 201:
                        result = response.json()
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Post #{result.get('post_id')} created successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    else:
                        st.error(f"Failed to create: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to API: {str(e)}")


with tab3:
    st.subheader("Update Existing Job Post")

    with st.form(f"update_post_form_{st.session_state.form_key_counter}"):
        update_id = st.number_input("Post ID to update *", min_value = 1, step = 1)
        new_title = st.text_input("New Job Title (leave blank to keep current)")
        new_duration = st.selectbox("New Duration", ["(keep current)"] + JOB_DURATION_OPTIONS)
        new_attendance = st.selectbox("New Attendance Type", ["(keep current)"] + ATTENDANCE_OPTIONS)
        new_salary = st.number_input("New Salary (0 to keep current)", min_value = 0.0, step = 5.0)
        new_city = st.text_input("New City (leave blank to keep current)")
        new_state = st.selectbox("New State", ["(keep current)"] + US_STATES)
        new_active = st.selectbox("Active Status", ["(keep current)", "Active", "Inactive"])
        new_job_link = st.text_input("Job Link (optional)", placeholder = "e.g., https://company.com/jobs/123")

        submitted = st.form_submit_button("Update Post")

        if submitted:
            payload = {}
            if new_title:
                payload["job_title"] = new_title
            if new_duration != "(keep current)":
                payload["job_duration"] = new_duration
            if new_attendance != "(keep current)":
                payload["attendance_type"] = new_attendance
            if new_salary > 0:
                payload["job_salary"] = new_salary
            if new_city and new_state != "(keep current)":
                payload["city_state"] = f"{new_city}, {new_state}"
            if new_active != "(keep current)":
                payload["is_active"] = 1 if new_active == "Active" else 0
            if new_job_link:
                payload["job_link"] = new_job_link

            if not payload:
                st.error("Please provide at least one field to update.")
            else:
                try:
                    response = requests.put(f"{BASE_URL}/{int(update_id)}", json=payload)
                    if response.status_code == 200:
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Post #{int(update_id)} updated successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    elif response.status_code == 404:
                        st.error("Post not found.")
                    else:
                        st.error(f"Failed: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to API: {str(e)}")


with tab4:
    st.subheader("Delete Job Post")
    st.warning("This action cannot be undone.")

    with st.form(f"delete_post_form_{st.session_state.form_key_counter}"):
        delete_id = st.number_input("Post ID to delete *", min_value = 1, step = 1)
        confirm   = st.checkbox("I understand this action is permanent")

        submitted = st.form_submit_button("Delete Post")

        if submitted:
            if not confirm:
                st.error("Please confirm before deleting.")
            else:
                try:
                    response = requests.delete(f"{BASE_URL}/{int(delete_id)}")
                    if response.status_code == 200:
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Post #{int(delete_id)} deleted successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    elif response.status_code == 404:
                        st.error("Post not found.")
                    else:
                        st.error(f"Failed: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to API: {str(e)}")


if st.session_state.show_success_modal:
    show_success_dialog(st.session_state.success_message)