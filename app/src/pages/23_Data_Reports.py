import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Data Reports")

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

API_URL = "http://web-api:4000/data_analyst/data_report"

tab1, tab2, tab3, tab4 = st.tabs(["View Reports", "Create Report", "Update Report", "Delete Report"])

with tab1:
    st.subheader("All Saved Reports")
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            reports = response.json()
            if reports:
                st.write(f"Found {len(reports)} reports")
                for report in reports:
                    with st.expander(f"Report #{report['report_id']} - {report.get('description', '')[:60]}"):
                        st.write(f"**Report ID:** {report['report_id']}")
                        st.write(f"**Description:** {report.get('description', 'N/A')}")
                        st.write(f"**Filter Criteria:** {report.get('filter_criteria', 'N/A')}")
                        st.write(f"**Created:** {report.get('created_at', 'N/A')}")
                        st.write(f"**Updated:** {report.get('updated_at', 'N/A')}")
                        st.write(f"**Creator ID:** {report.get('creator_id', 'N/A')}")
            else:
                st.info("No reports saved yet.")
        else:
            st.error(f"Failed to fetch reports: {response.status_code}")
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to the API: {str(e)}")

with tab2:
    st.subheader("Create New Report")

    with st.form(f"create_report_form_{st.session_state.form_key_counter}"):
        description = st.text_area("Description *", placeholder="Summary of the report...")
        filter_criteria = st.text_area("Filter Criteria *", placeholder="e.g., major=CS, industry=Tech")
        creator_id = st.number_input("Creator (Admin) ID *", min_value=1, step=1)

        submitted = st.form_submit_button("Create Report")

        if submitted:
            if not all([description, filter_criteria, creator_id]):
                st.error("Please fill in all required fields marked with *")
            else:
                report_data = {
                    "description": description,
                    "filter_criteria": filter_criteria,
                    "creator_id": int(creator_id),
                }
                try:
                    response = requests.post(API_URL, json=report_data)
                    if response.status_code == 201:
                        result = response.json()
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Report #{result.get('report_id')} created successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    else:
                        st.error(f"Failed to create: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the API: {str(e)}")

with tab3:
    st.subheader("Update Existing Report")

    with st.form(f"update_report_form_{st.session_state.form_key_counter}"):
        update_id = st.number_input("Report ID to update *", min_value=1, step=1)
        new_description = st.text_area("New Description (leave blank to keep current)")
        new_filter = st.text_area("New Filter Criteria (leave blank to keep current)")

        submitted = st.form_submit_button("Update Report")

        if submitted:
            payload = {}
            if new_description:
                payload["description"] = new_description
            if new_filter:
                payload["filter_criteria"] = new_filter

            if not payload:
                st.error("Please provide at least one field to update.")
            else:
                try:
                    response = requests.put(f"{API_URL}/{int(update_id)}", json=payload)
                    if response.status_code == 200:
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Report #{int(update_id)} updated successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    elif response.status_code == 404:
                        st.error("Report not found.")
                    else:
                        st.error(f"Failed: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the API: {str(e)}")

with tab4:
    st.subheader("Delete Report")
    st.warning("This action cannot be undone.")

    with st.form(f"delete_report_form_{st.session_state.form_key_counter}"):
        delete_id = st.number_input("Report ID to delete *", min_value=1, step=1)
        confirm = st.checkbox("I understand this action is permanent")

        submitted = st.form_submit_button("Delete Report")

        if submitted:
            if not confirm:
                st.error("Please confirm before deleting.")
            else:
                try:
                    response = requests.delete(f"{API_URL}/{int(delete_id)}")
                    if response.status_code == 200:
                        st.session_state.show_success_modal = True
                        st.session_state.success_message = f"Report #{int(delete_id)} deleted successfully!"
                        st.session_state.reset_form = True
                        st.rerun()
                    elif response.status_code == 404:
                        st.error("Report not found.")
                    else:
                        st.error(f"Failed: {response.json().get('error', 'Unknown error')}")
                except requests.exceptions.RequestException as e:
                    st.error(f"Error connecting to the API: {str(e)}")

if st.session_state.show_success_modal:
    show_success_dialog(st.session_state.success_message)
    