import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Analytics Dashboard")

API_URL = "http://web-api:4000/data_analyst/application"

col1, col2, col3, col4 = st.columns(4)

try:
    response = requests.get(API_URL)
    if response.status_code == 200:
        applications = response.json()


        majors = sorted(list(set(a["major"] for a in applications if a.get("major"))))
        industries = sorted(list(set(a["industry"] for a in applications if a.get("industry"))))
        stages = sorted(list(set(a["stage"] for a in applications if a.get("stage"))))

        import re
        def extract_year(date_str):
            match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
            return match.group(0) if match else None
        grad_years = sorted(list(set(
            extract_year(a["graduation_year"]) for a in applications
            if a.get("graduation_year") and extract_year(a["graduation_year"])
        )))

        with col1:
            selected_major = st.selectbox("Filter by Major", ["All"] + majors)

        with col2:
            selected_industry = st.selectbox("Filter by Industry", ["All"] + industries)

        with col3:
            selected_stage = st.selectbox("Filter by Stage", ["All"] + stages)

        with col4:
            selected_year = st.selectbox("Filter by Graduation Year", ["All"] + grad_years)

        params = {}
        if selected_major != "All":
            params["major"] = selected_major
        if selected_industry != "All":
            params["industry"] = selected_industry
        if selected_stage != "All":
            params["stage"] = selected_stage
        if selected_year != "All":
            params["grad_year"] = selected_year

        filtered_response = requests.get(API_URL, params=params)
        if filtered_response.status_code == 200:
            filtered_apps = filtered_response.json()

            st.write(f"Found {len(filtered_apps)} applications")

            for app in filtered_apps:
                with st.expander(
                    f"Application #{app['application_id']} - {app.get('major', 'N/A')} "
                    f"| {app.get('industry', 'N/A')} | {app.get('stage', 'N/A')}"
                ):
                    info_col, status_col = st.columns(2)

                    with info_col:
                        st.write("**Applicant Info**")
                        st.write(f"**Major:** {app.get('major', 'N/A')}")
                        st.write(f"**Graduation Year:** {extract_year(app.get('graduation_year', '')) or 'N/A'}")
                        st.write(f"**Application Date:** {app.get('application_date', 'N/A')}")

                    with status_col:
                        st.write(f"**Industry:** {app.get('industry', 'N/A')}")
                        st.write(f"**Stage:** {app.get('stage', 'N/A')}")
                        st.write(f"**Status:** {app.get('status', 'N/A')}")

                    if app.get('cover_letter'):
                        st.write("**Cover Letter**")
                        st.write(app['cover_letter'])

    else:
        st.error("Failed to fetch application data from the API")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running on http://web-api:4000")