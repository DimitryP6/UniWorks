import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title('Browse Jobs')

API_BASE = 'http://web-api:4000'

col1, col2, col3, col4 = st.columns(4)
with col1:
    title_filter = st.text_input('Job Title')
with col2:
    location_filter = st.text_input('Location')
with col3:
    salary_filter = st.number_input('Min Salary', min_value=0, value=0, step=1000)
with col4:
    attendance_filter = st.selectbox('Work Type', ['Any', 'remote', 'hybrid', 'on-site'])

params = {}
if title_filter:
    params['title'] = title_filter
if location_filter:
    params['location'] = location_filter
if salary_filter > 0:
    params['salary'] = salary_filter
if attendance_filter != 'Any':
    params['attendance_type'] = attendance_filter

try:
    response = requests.get(f'{API_BASE}/job_post', params=params)
    if response.status_code == 200:
        jobs = response.json()
        st.write(f'**{len(jobs)} job(s) found**')
        for job in jobs:
            with st.expander(f"{job.get('title', 'Untitled')} — {job.get('location', 'N/A')} ({job.get('attendance_type', '')})"):
                left, right = st.columns(2)
                with left:
                    st.write(f"**Salary:** ${job.get('salary', 'N/A'):,}" if isinstance(job.get('salary'), (int, float)) else f"**Salary:** {job.get('salary', 'N/A')}")
                    st.write(f"**Location:** {job.get('location', 'N/A')}")
                    st.write(f"**Work Type:** {job.get('attendance_type', 'N/A')}")
                with right:
                    st.write(f"**Description:** {job.get('description', 'No description available.')}")
                if st.button('Apply', key=f"apply_{job.get('post_id')}"):
                    st.session_state['selected_job_id'] = job.get('post_id')
                    st.switch_page('pages/42_My_Applications.py')
    else:
        st.error('Failed to fetch job listings.')
except requests.exceptions.RequestException as e:
    st.error(f'Error connecting to API: {e}')
    st.info('Please ensure the API server is running on http://web-api:4000')
