import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Applications by Job Post")

JOB_POST_URL = "http://web-api:4000/job_poster/job_post"


st.subheader("Search by Job Post ID")
col1, col2 = st.columns([2, 1])
with col1:
    post_id = st.number_input("Job Post ID", min_value = 1, step = 1, label_visibility = "collapsed")
with col2:
    search = st.button("Search", use_container_width=True)

if search:
    try:
        post_response = requests.get(f"{JOB_POST_URL}/{int(post_id)}")
        if post_response.status_code == 404:
            st.error(f"Job post #{int(post_id)} not found.")
            st.stop()
        elif post_response.status_code != 200:
            st.error(f"Failed to fetch job post: {post_response.status_code}")
            st.stop()

        post = post_response.json()

        st.markdown("---")
        st.subheader(f"{post.get('job_title', 'N/A')} — Post #{post_id}")
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.write(f"**Company:** {post.get('company_name', 'N/A')}")
            st.write(f"**Industry:** {post.get('industry', 'N/A')}")
        with info_col2:
            st.write(f"**Location:** {post.get('city_state', 'N/A')}")
            st.write(f"**Attendance:** {post.get('attendance_type', 'N/A')}")
        with info_col3:
            st.write(f"**Duration:** {post.get('job_duration', 'N/A')}")
            st.write(f"**Salary:** {post.get('job_salary', 'N/A')}")

        st.markdown("---")

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")
        st.stop()

    try:
        apps_response = requests.get(f"{JOB_POST_URL}/{int(post_id)}/applications")
        if apps_response.status_code == 200:
            apps = apps_response.json()
            if apps:
                st.write(f"Found **{len(apps)}** application(s)")

                for app in apps:
                    with st.expander(
                        f"Application #{app['application_id']} — "
                        f"{app.get('full_name', 'N/A')} | "
                        f"{app.get('stage', 'N/A')} | "
                        f"{app.get('status', 'N/A')}"
                    ):
                        col_left, col_right = st.columns(2)

                        with col_left:
                            st.write("**Applicant Info**")
                            st.write(f"**Name:** {app.get('full_name', 'N/A')}")
                            st.write(f"**Email:** {app.get('email', 'N/A')}")
                            st.write(f"**Phone:** {app.get('phone_number', 'N/A')}")
                            st.write(f"**Location:** {app.get('city_state', 'N/A')}")
                            st.write(f"**Major:** {app.get('major', 'N/A')}")
                            st.write(f"**Degree:** {app.get('degree_level', 'N/A')}")
                            st.write(f"**Graduation Year:** {app.get('graduation_year', 'N/A')}")

                        with col_right:
                            st.write("**Application Status**")
                            st.write(f"**Stage:** {app.get('stage', 'N/A')}")
                            st.write(f"**Status:** {app.get('status', 'N/A')}")
                            st.write(f"**Applied On:** {app.get('application_date', 'N/A')}")

                        if app.get('cover_letter'):
                            st.write("**Cover Letter**")
                            st.write(app['cover_letter'])

                        if app.get('education') or app.get('work_experience') or app.get('personal_project'):
                            st.write("**Resume**")
                            if app.get('education'):
                                st.write(f"*Education:* {app['education']}")
                            if app.get('work_experience'):
                                st.write(f"*Work Experience:* {app['work_experience']}")
                            if app.get('personal_project'):
                                st.write(f"*Projects:* {app['personal_project']}")
            else:
                st.info(f"No applications found for job post #{int(post_id)}.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to API: {str(e)}")