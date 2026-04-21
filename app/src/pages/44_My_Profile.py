import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('My Profile')

API_BASE = 'http://web-api:4000'
seeker_id = st.session_state.get('seeker_id', 1)

try:
    response = requests.get(f'{API_BASE}/job_seeker/{seeker_id}')
    if response.status_code == 200:
        profile = response.json()

        st.write('### Profile Information')
        with st.form('profile_form'):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input('Name', value=profile.get('name', ''))
                email = st.text_input('Email', value=profile.get('email', ''))
                major = st.text_input('Major', value=profile.get('major', ''))
                grad_year = st.number_input('Graduation Year', value=int(profile.get('grad_year') or 2025), step=1)
            with col2:
                occupation = st.text_input('Occupation', value=profile.get('occupation', ''))
                education = st.text_input('Education', value=profile.get('education', ''))
                location = st.text_input('Location', value=profile.get('location', ''))
            if st.form_submit_button('Save Changes', type='primary'):
                payload = {
                    'name': name, 'email': email, 'major': major, 'grad_year': grad_year,
                    'occupation': occupation, 'education': education, 'location': location
                }
                r = requests.put(f'{API_BASE}/job_seeker/{seeker_id}', json=payload)
                if r.status_code == 200:
                    st.success('Profile updated!')
                else:
                    st.error(f'Failed to update: {r.json().get("error", "Unknown error")}')
    elif response.status_code == 404:
        st.warning('Profile not found.')
    else:
        st.error('Failed to fetch profile.')
except requests.exceptions.RequestException as e:
    st.error(f'Error connecting to API: {e}')
    st.info('Please ensure the API server is running on http://web-api:4000')

st.divider()
st.write('### Resume Management')

col1, col2 = st.columns(2)

with col1:
    st.write('**Add Resume**')
    with st.form('add_resume_form'):
        resume_text = st.text_area('Resume Text', height=200)
        if st.form_submit_button('Upload Resume', type='primary'):
            try:
                r = requests.post(f'{API_BASE}/job_seeker/resume', json={'seeker_id': seeker_id, 'resume_text': resume_text})
                if r.status_code == 201:
                    st.success(f"Resume added (ID: {r.json().get('resume_id')})")
                else:
                    st.error(f'Failed: {r.json().get("error", "Unknown error")}')
            except requests.exceptions.RequestException as e:
                st.error(f'Error: {e}')

with col2:
    st.write('**Update / Delete Resume**')
    resume_id_input = st.number_input('Resume ID', min_value=1, step=1, key='mgmt_resume_id')
    updated_text = st.text_area('Updated Resume Text', height=150, key='updated_resume_text')
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button('Update', use_container_width=True):
            try:
                r = requests.put(f'{API_BASE}/job_seeker/resume/{resume_id_input}', json={'resume_text': updated_text})
                if r.status_code == 200:
                    st.success('Resume updated!')
                else:
                    st.error(f'Failed: {r.json().get("error", "Unknown error")}')
            except requests.exceptions.RequestException as e:
                st.error(f'Error: {e}')
    with btn_col2:
        if st.button('Delete', use_container_width=True):
            try:
                r = requests.delete(f'{API_BASE}/job_seeker/resume/{resume_id_input}')
                if r.status_code == 200:
                    st.success('Resume deleted.')
                else:
                    st.error(f'Failed: {r.json().get("error", "Unknown error")}')
            except requests.exceptions.RequestException as e:
                st.error(f'Error: {e}')
