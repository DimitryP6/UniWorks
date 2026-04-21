import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Application Trends")
st.write("See aggregated application trends across majors, industries, and stages.")

API_URL = "http://web-api:4000/data_analyst/application/trends"
APP_URL = "http://web-api:4000/data_analyst/application"

col1, col2, col3, col4 = st.columns(4)

try:
    all_apps_response = requests.get(APP_URL)
    if all_apps_response.status_code == 200:
        all_apps = all_apps_response.json()

        majors = sorted(list(set(a["major"] for a in all_apps if a.get("major"))))
        industries = sorted(list(set(a["industry"] for a in all_apps if a.get("industry"))))
        stages = sorted(list(set(a["stage"] for a in all_apps if a.get("stage"))))
        import re
        def extract_year(date_str):
            match = re.search(r'\b(19|20)\d{2}\b', str(date_str))
            return match.group(0) if match else None
        grad_years = sorted(list(set(
            extract_year(a["graduation_year"]) for a in all_apps
            if a.get("graduation_year") and extract_year(a["graduation_year"])
        )))

        with col1:
            selected_major = st.selectbox("Filter by Major", ["All"] + majors)
        with col2:
            selected_industry = st.selectbox("Filter by Industry", ["All"] + industries)
        with col3:
            selected_year = st.selectbox("Filter by Graduation Year", ["All"] + grad_years)
        with col4:
            selected_stage = st.selectbox("Filter by Stage", ["All"] + stages)

        params = {}
        if selected_major != "All":
            params["major"] = selected_major
        if selected_industry != "All":
            params["industry"] = selected_industry
        if selected_year != "All":
            params["grad_year"] = selected_year
        if selected_stage != "All":
            params["stage"] = selected_stage

        trends_response = requests.get(API_URL, params=params)
        if trends_response.status_code == 200:
            trends = trends_response.json()

            if trends:
                df = pd.DataFrame(trends)
                st.write(f"Found {len(df)} trend groups")

                st.subheader("Trend Data")
                st.dataframe(df, use_container_width=True)

                st.write("---")
                st.subheader("Visual Summary")

                chart_col1, chart_col2 = st.columns(2)

                with chart_col1:
                    st.write("**Applications by Major**")
                    if 'major' in df.columns:
                        major_totals = df.groupby('major')['total_applications'].sum()
                        st.bar_chart(major_totals)

                with chart_col2:
                    st.write("**Applications by Industry**")
                    if 'industry' in df.columns:
                        industry_totals = df.groupby('industry')['total_applications'].sum()
                        st.bar_chart(industry_totals)

                st.write("**Applications by Stage**")
                if 'stage' in df.columns:
                    stage_totals = df.groupby('stage')['total_applications'].sum()
                    st.bar_chart(stage_totals)
            else:
                st.info("No trends match these filters.")
        else:
            st.error(f"Failed to fetch trends: {trends_response.status_code}")

    else:
        st.error("Failed to fetch application data from the API")

except requests.exceptions.RequestException as e:
    st.error(f"Error connecting to the API: {str(e)}")
    st.info("Please ensure the API server is running on http://web-api:4000")