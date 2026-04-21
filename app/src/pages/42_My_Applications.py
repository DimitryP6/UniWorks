import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('My Applications')

API_BASE = 'http://web-api:4000'
seeker_id = st.session_state.get('seeker_id', 1)

# --- Submit new application if arriving from Browse Jobs ---
if 'selected_job_id' in st.session_state:
    st.write('### Submit Application')
    job_id = st.session_state['selected_job_id']
    st.write(f'**Job ID:** {job_id}')
    resume_id = st.number_input('Resume ID', min_value=1, step=1)
    cover_letter = st.text_area('Cover Letter')
    if st.button('Submit Application', type='primary'):
        payload = {
            'seeker_id': seeker_id,
            'job_id': job_id,
            'resume_id': resume_id,
            'cover_letter': cover_letter,
        }
        try:
            r = requests.post(f'{API_BASE}/application', json=payload)
            if r.status_code == 201:
                st.success('Application submitted!')
                del st.session_state['selected_job_id']
                st.rerun()
            else:
                st.error(f'Failed to submit: {r.json().get("error", "Unknown error")}')
        except requests.exceptions.RequestException as e:
            st.error(f'Error: {e}')
    if st.button('Cancel'):
        del st.session_state['selected_job_id']
        st.rerun()
    st.divider()

# --- Application status list ---
st.write('### Application Status')
try:
    response = requests.get(f'{API_BASE}/job_seeker/{seeker_id}/application_status')
    if response.status_code == 200:
        applications = response.json()
        if not applications:
            st.info('No applications yet. Browse jobs to get started!')
        else:
            for app in applications:
                status_color = {'pending': '🟡', 'accepted': '🟢', 'rejected': '🔴'}.get(app.get('status', ''), '⚪')
                with st.expander(f"{status_color} {app.get('title', 'Unknown Job')} — {app.get('status', 'N/A').capitalize()}"):
                    st.write(f"**Stage:** {app.get('stage', 'N/A')}")
                    st.write(f"**Applied:** {app.get('application_date', 'N/A')}")
                    if st.button('Withdraw', key=f"del_{app.get('application_id')}"):
                        try:
                            dr = requests.delete(f"{API_BASE}/application/{app.get('application_id')}")
                            if dr.status_code == 200:
                                st.success('Application withdrawn.')
                                st.rerun()
                            else:
                                st.error('Failed to withdraw application.')
                        except requests.exceptions.RequestException as e:
                            st.error(f'Error: {e}')
    else:
        st.error('Failed to fetch applications.')
except requests.exceptions.RequestException as e:
    st.error(f'Error connecting to API: {e}')
    st.info('Please ensure the API server is running on http://web-api:4000')
