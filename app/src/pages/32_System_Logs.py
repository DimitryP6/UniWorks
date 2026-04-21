import streamlit as st
import requests
from datetime import date

API_BASE = "http://api:4000"

st.set_page_config(page_title="System Logs", layout="wide")
st.title("System Logs")
st.write("Monitor system errors and track resolution status.")

# ------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    status_filter = st.selectbox("Resolution Status", ["All", "open", "resolved"])
    error_code_filter = st.text_input("Error Code (partial match)")
    from_date = st.date_input("Resolved from", value=None)
    to_date   = st.date_input("Resolved to",   value=None)

params = {}
if status_filter != "All":
    params["status"] = status_filter
if error_code_filter:
    params["error_code"] = error_code_filter
if from_date:
    params["from"] = str(from_date)
if to_date:
    params["to"] = str(to_date)

# ------------------------------------------------------------
# Fetch and display logs
# ------------------------------------------------------------
try:
    response = requests.get(f"{API_BASE}/system_log/", params=params)
    logs = response.json()

    if not logs:
        st.info("No log entries found.")
    else:
        st.subheader(f"{len(logs)} log entry(ies)")
        st.dataframe(
            logs,
            use_container_width=True,
            column_order=["log_id", "error_code", "error_description",
                          "resolution_status", "resolved_at", "creator_name"],
        )
except Exception as e:
    st.error(f"Could not load logs: {e}")

st.divider()

# ------------------------------------------------------------
# Mark a log as resolved
# ------------------------------------------------------------
st.subheader("Mark Log as Resolved")

log_id_resolve = st.number_input("Log ID to resolve", min_value=1, step=1, key="resolve_id")
resolved_date  = st.date_input("Resolved on", value=date.today(), key="resolve_date")

if st.button("Mark as Resolved", type="primary"):
    try:
        res = requests.put(
            f"{API_BASE}/system_log/{int(log_id_resolve)}",
            json={"resolution_status": "resolved", "resolved_at": str(resolved_date)},
        )
        st.success(res.json().get("message", "Log updated."))
    except Exception as e:
        st.error(f"Error: {e}")

st.divider()

# ------------------------------------------------------------
# Add a new log entry
# ------------------------------------------------------------
st.subheader("Add New Log Entry")

with st.form("new_log_form"):
    error_code        = st.text_input("Error Code",        placeholder="e.g. DUP_APP")
    error_description = st.text_area("Error Description",  placeholder="Describe the issue...")
    resolution_status = st.selectbox("Status", ["open", "resolved"])
    creator_id        = st.number_input("Your Admin ID", min_value=1, step=1)
    resolved_at       = st.date_input("Resolved At (optional)", value=None)
    submitted         = st.form_submit_button("Add Log Entry")

if submitted:
    if not error_code or not error_description or not creator_id:
        st.warning("Error code, description, and admin ID are required.")
    else:
        payload = {
            "error_code":        error_code,
            "error_description": error_description,
            "resolution_status": resolution_status,
            "creator_id":        int(creator_id),
            "resolved_at":       str(resolved_at) if resolved_at else None,
        }
        try:
            res = requests.post(f"{API_BASE}/system_log/", json=payload)
            data = res.json()
            st.success(f"Log created — ID: {data.get('log_id')}")
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ------------------------------------------------------------
# Duplicate application detector
# ------------------------------------------------------------
st.subheader("Duplicate Application Detector")
st.write("Identify applicants who submitted the same job more than once.")

if st.button("Scan for Duplicates"):
    try:
        res = requests.get(f"{API_BASE}/system_log/duplicates")
        dupes = res.json()
        if not dupes:
            st.success("No duplicate applications found.")
        else:
            st.warning(f"{len(dupes)} duplicate group(s) found.")
            st.dataframe(dupes, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
