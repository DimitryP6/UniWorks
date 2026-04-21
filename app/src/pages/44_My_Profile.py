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
                st.text_input('Name', value=profile.get('full_name', ''), disabled=True)
                st.text_input('Email', value=profile.get('email', ''), disabled=True)
                major = st.text_input('Major', value=profile.get('major', '') or '')
                university = st.text_input('University', value=profile.get('university', '') or '')
            with col2:
                city_state = st.text_input('City/State', value=profile.get('city_state', '') or '')
                phone_number = st.text_input('Phone Number', value=profile.get('phone_number', '') or '')
                degree_options = ['Bachelors', 'Masters', 'PHD']
                current_degree = profile.get('degree_level', 'Bachelors')
                degree_level = st.selectbox(
                    'Degree Level',
                    degree_options,
                    index=degree_options.index(current_degree) if current_degree in degree_options else 0
                )

            if st.form_submit_button('Save Changes', type='primary'):
                payload = {
                    'major': major,
                    'university': university,
                    'city_state': city_state,
                    'phone_number': phone_number,
                    'degree_level': degree_level,
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
        education = st.text_area('Education', height=80)
        work_experience = st.text_area('Work Experience', height=80)
        personal_project = st.text_area('Personal Projects', height=80)
        hobby = st.text_input('Hobbies')
        if st.form_submit_button('Upload Resume', type='primary'):
            try:
                payload = {
                    'seeker_id': seeker_id,
                    'education': education,
                    'work_experience': work_experience,
                    'personal_project': personal_project,
                    'hobby': hobby
                }
                r = requests.post(f'{API_BASE}/job_seeker/resume', json=payload)
                if r.status_code == 201:
                    st.success(f"Resume added (ID: {r.json().get('resume_id')})")
                else:
                    st.error(f'Failed: {r.json().get("error", "Unknown error")}')
            except requests.exceptions.RequestException as e:
                st.error(f'Error: {e}')

with col2:
    st.write('**Update / Delete Resume**')
    resume_id_input = st.number_input('Resume ID', min_value=1, step=1, key='mgmt_resume_id')

    # Show current resume if exists
    if st.button('Load Resume', key='load_resume'):
        try:
            r = requests.get(f'{API_BASE}/job_seeker/resume/{resume_id_input}')
            if r.status_code == 200:
                st.session_state['loaded_resume'] = r.json()
            else:
                st.warning('Resume not found')
                st.session_state.pop('loaded_resume', None)
        except requests.exceptions.RequestException as e:
            st.error(f'Error: {e}')

    if 'loaded_resume' in st.session_state:
        lr = st.session_state['loaded_resume']
        with st.form('update_resume_form'):
            new_education = st.text_area('Education', value=lr.get('education', '') or '', height=80)
            new_work = st.text_area('Work Experience', value=lr.get('work_experience', '') or '', height=80)
            new_project = st.text_area('Personal Projects', value=lr.get('personal_project', '') or '', height=80)
            new_hobby = st.text_input('Hobbies', value=lr.get('hobby', '') or '')

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.form_submit_button('Update', use_container_width=True):
                    payload = {
                        'education': new_education,
                        'work_experience': new_work,
                        'personal_project': new_project,
                        'hobby': new_hobby
                    }
                    try:
                        r = requests.put(f'{API_BASE}/job_seeker/resume/{resume_id_input}', json=payload)
                        if r.status_code == 200:
                            st.success('Resume updated!')
                            st.session_state.pop('loaded_resume', None)
                        else:
                            st.error(f'Failed: {r.json().get("error", "Unknown error")}')
                    except requests.exceptions.RequestException as e:
                        st.error(f'Error: {e}')
            with btn_col2:
                if st.form_submit_button('Delete', use_container_width=True):
                    try:
                        # Note: job_seeker_routes.py should have a DELETE /resume/{id} endpoint
                        # If it doesn't, this will fail
                        r = requests.delete(f'{API_BASE}/job_seeker/resume/{resume_id_input}')
                        if r.status_code == 200:
                            st.success('Resume deleted.')
                            st.session_state.pop('loaded_resume', None)
                        else:
                            st.error(f'Failed: {r.json().get("error", "Unknown error")}')
                    except requests.exceptions.RequestException as e:
                        st.error(f'Error: {e}')