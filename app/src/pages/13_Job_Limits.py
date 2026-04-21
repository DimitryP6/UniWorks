import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Job Limits")

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

if st.session_state.reset_form:
    st.session_state.form_key_counter += 1
    st.session_state.reset_form = False

BASE_URL = "http://web-api:4000/job_poster/job_post"

tab1, tab2, tab3 = st.tabs(["View Limits", "Add Limit", "Update Limit"])


with tab1:
    st.subheader("View Job Limits by Post ID")

    col1, col2 = st.columns([2, 1])
    with col1:
        view_post_id = st.number_input("Job Post ID", min_value = 1, step = 1,
                                        key = "view_post_id", label_visibility = "collapsed")
    with col2:
        search = st.button("Search", use_container_width = True, key = "view_search")

    if search:
        try:
            response = requests.get(f"{BASE_URL}/{int(view_post_id)}/job_limit")
            if response.status_code == 200:
                limits = response.json()
                if limits:
                    st.write(f"Found **{len(limits)}** limit(s) for post #{int(view_post_id)}")
                    for limit in limits:
                        with st.expander(f"Limit #{limit['limit_id']}"):
                            col_left, col_right = st.columns(2)
                            with col_left:
                                st.write(f"**Max Applications:** {limit.get('max_count', 'N/A')}")
                                st.write(f"**Min GPA:** {limit.get('min_gpa', 'N/A')}")
                            with col_right:
                                st.write(f"**University:** {limit.get('university', 'N/A')}")
                                st.write(f"**College:** {limit.get('college', 'N/A')}")
                else:
                    st.info(f"No limits found for post #{int(view_post_id)}.")
            elif response.status_code == 404:
                st.error(f"Job post #{int(view_post_id)} not found.")
            else:
                st.error(f"Failed to fetch limits: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to API: {str(e)}")


with tab2:
    st.subheader("Add Limit to a Job Post")

    with st.form(f"add_limit_form_{st.session_state.form_key_counter}"):
        post_id = st.number_input("Job Post ID *", min_value = 1, step = 1)
        max_count = st.number_input("Max Applications (optional)", min_value = 0, step = 1)
        min_gpa = st.number_input("Minimum GPA (optional)", min_value = 0.0,
                                       max_value = 4.0, step = 0.1)
        university = st.text_input("University Restriction (optional)",
                                     placeholder = "e.g., Northeastern University")
        college = st.text_input("College/Field Restriction (optional)",
                                     placeholder = "e.g., Khoury College of Computer Sciences")

        submitted = st.form_submit_button("Add Limit")

        if submitted:
            if not post_id:
                st.error("Please provide a Job Post ID.")
            else:
                limit_data = {
                    "max_count": int(max_count) if max_count > 0 else None,
                    "min_gpa": float(min_gpa) if min_gpa > 0 else None,
                    "university": university if university else None,
                    "college": college if college else None,
                }
                try:
                    response = requests.post(
                        f"{BASE_URL}/{int(post_id)}/job_limit",
                        json=limit_data
                    )
                    if response.status_code == 201:
                        result = response.json()
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Limit #{result.get('limit_id')} added successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    elif response.status_code == 404:
                        st.error(f"Job post #{int(post_id)} not found.")
                    else:
                        st.error(f"Failed to add limit: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to API: {str(e)}")


with tab3:
    st.subheader("Update Existing Job Limit")
 
    with st.form(f"update_limit_form_{st.session_state.form_key_counter}"):
        update_post_id = st.number_input("Job Post ID *", min_value = 1, step = 1)
        new_max_count = st.number_input("Max Applications (0 to nullify)",
                                           min_value = 0, step = 1)
        new_min_gpa = st.number_input("Minimum GPA (0 to nullify)",
                                           min_value = 0.0, max_value = 4.0, step = 0.1)
        new_university = st.text_input("University Restriction (leave blank to remove)")
        new_college = st.text_input("College Restriction (leave blank to remove)")
 
        submitted = st.form_submit_button("Update Limit")
 
        if submitted:
            payload = {
                "max_count": int(new_max_count) if new_max_count > 0 else None,
                "min_gpa": float(new_min_gpa) if new_min_gpa > 0 else None,
                "university": new_university if new_university else None,
                "college": new_college if new_college else None,
            }
            try:
                response = requests.put(
                    f"{BASE_URL}/{int(update_post_id)}/job_limit",
                    json=payload
                )
                if response.status_code == 200:
                    st.session_state.show_success_modal = True
                    st.session_state.success_message = f"Limit for post #{int(update_post_id)} updated successfully!"
                    st.session_state.reset_form = True
                    st.rerun()
                elif response.status_code == 404:
                    st.error(f"Job limit for post #{int(update_post_id)} not found.")
                else:
                    st.error(f"Failed to update: {response.json().get('error', 'Unknown error')}")
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to API: {str(e)}")


if st.session_state.show_success_modal:
    show_success_dialog(st.session_state.success_message)