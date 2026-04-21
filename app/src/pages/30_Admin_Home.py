import streamlit as st
import requests
from modules.nav import SideBarLinks

API_BASE = "http://api:4000"

# Redirect if not authenticated as administrator
if not st.session_state.get('authenticated') or st.session_state.get('role') != 'administrator':
    st.switch_page('Home.py')

SideBarLinks()

st.title(f"Welcome, {st.session_state.get('first_name', 'Admin')} 👋")
st.write("System Administrator Dashboard — UniWorks platform overview.")

st.divider()

# ------------------------------------------------------------
# Quick stats row
# ------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

try:
    users = requests.get(f"{API_BASE}/user/").json()
    active_users   = sum(1 for u in users if u.get("is_active") == 1)
    inactive_users = sum(1 for u in users if u.get("is_active") == 0)
except:
    active_users = inactive_users = "—"

try:
    logs = requests.get(f"{API_BASE}/system_log/").json()
    open_logs     = sum(1 for l in logs if l.get("resolution_status") == "open")
    resolved_logs = sum(1 for l in logs if l.get("resolution_status") == "resolved")
except:
    open_logs = resolved_logs = "—"

with col1:
    st.metric("Active Users", active_users)
with col2:
    st.metric("Inactive Users", inactive_users)
with col3:
    st.metric("Open Issues", open_logs)
with col4:
    st.metric("Resolved Issues", resolved_logs)

st.divider()

# ------------------------------------------------------------
# Recent system logs
# ------------------------------------------------------------
st.subheader("Recent System Logs")

try:
    recent_logs = requests.get(f"{API_BASE}/system_log/", params={"status": "open"}).json()
    if not recent_logs:
        st.success("No open issues — system is healthy.")
    else:
        st.warning(f"{len(recent_logs)} open issue(s) need attention.")
        st.dataframe(
            recent_logs[:5],
            use_container_width=True,
            column_order=["log_id", "error_code", "error_description",
                          "resolution_status", "creator_name"],
        )
except Exception as e:
    st.error(f"Could not load logs: {e}")

st.divider()

# ------------------------------------------------------------
# Quick navigation
# ------------------------------------------------------------
st.subheader("Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Manage Users", use_container_width=True):
        st.switch_page("pages/31_User_Management.py")

with col2:
    if st.button("View System Logs", use_container_width=True):
        st.switch_page("pages/32_System_Logs.py")

with col3:
    if st.button("Manage Admins", use_container_width=True):
        st.switch_page("pages/33_Admin_Management.py")
