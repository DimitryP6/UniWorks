import streamlit as st
import requests

API_BASE = "http://api:4000"

st.set_page_config(page_title="User Management", layout="wide")
st.title("User Management")
st.write("View, filter, and manage all platform users.")

# ------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    user_type = st.selectbox(
        "User Type",
        ["All", "job_seeker", "job_poster", "admin"],
    )
    is_active = st.selectbox("Status", ["All", "Active", "Inactive"])
    inactive_before = st.date_input("Inactive before", value=None)

# Build query params
params = {}
if user_type != "All":
    params["user_type"] = user_type
if is_active == "Active":
    params["is_active"] = 1
elif is_active == "Inactive":
    params["is_active"] = 0
if inactive_before:
    params["inactive_before"] = str(inactive_before)

# ------------------------------------------------------------
# Fetch and display users
# ------------------------------------------------------------
try:
    response = requests.get(f"{API_BASE}/user/", params=params)
    users = response.json()

    if not users:
        st.info("No users found matching the selected filters.")
    else:
        st.subheader(f"{len(users)} user(s) found")
        st.dataframe(
            users,
            use_container_width=True,
            column_order=["user_id", "full_name", "email", "user_type", "is_active", "last_login"],
        )

except Exception as e:
    st.error(f"Could not load users: {e}")

st.divider()

# ------------------------------------------------------------
# Archive inactive users
# ------------------------------------------------------------
st.subheader("Archive Inactive Users")
st.write("Set `is_active = 0` for all users who have not logged in since a given date.")

archive_date = st.date_input("Archive users inactive before", key="archive_date")

if st.button("Archive Users", type="primary"):
    if archive_date:
        try:
            res = requests.put(
                f"{API_BASE}/user/",
                json={"inactive_before": str(archive_date)},
            )
            data = res.json()
            st.success(f"{data.get('rows_affected', 0)} user(s) archived.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please select a date first.")

st.divider()

# ------------------------------------------------------------
# Edit individual user
# ------------------------------------------------------------
st.subheader("Edit a User Record")
st.write("Update profile fields or fix incomplete records.")

user_id_input = st.number_input("Enter User ID to edit", min_value=1, step=1)

if st.button("Load User"):
    try:
        res = requests.get(f"{API_BASE}/user/{int(user_id_input)}")
        if res.status_code == 404:
            st.warning("User not found.")
        else:
            user = res.json()
            st.session_state["loaded_user"] = user
    except Exception as e:
        st.error(f"Error: {e}")

if "loaded_user" in st.session_state:
    u = st.session_state["loaded_user"]
    st.write(f"Editing: **{u.get('full_name')}** ({u.get('email')})")

    col1, col2 = st.columns(2)
    with col1:
        new_major       = st.text_input("Major",        value=u.get("major", "") or "")
        new_city        = st.text_input("City / State", value=u.get("city_state", "") or "")
        new_degree      = st.text_input("Degree Level", value=u.get("degree_level", "") or "")
    with col2:
        new_phone       = st.text_input("Phone Number", value=u.get("phone_number", "") or "")
        new_is_active   = st.selectbox("Is Active", [1, 0],
                                        index=0 if u.get("is_active") else 1)

    if st.button("Save Changes", type="primary"):
        payload = {
            "major":        new_major,
            "city_state":   new_city,
            "degree_level": new_degree,
            "phone_number": new_phone,
            "is_active":    new_is_active,
        }
        try:
            res = requests.put(f"{API_BASE}/user/{int(user_id_input)}", json=payload)
            st.success(res.json().get("message", "Updated successfully."))
            del st.session_state["loaded_user"]
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ------------------------------------------------------------
# Validate incomplete records
# ------------------------------------------------------------
st.subheader("Incomplete Records")
st.write("Job seeker profiles with missing required fields.")

if st.button("Run Validation Check"):
    try:
        res = requests.get(f"{API_BASE}/user/validate")
        rows = res.json()
        if not rows:
            st.success("All records are complete!")
        else:
            st.warning(f"{len(rows)} incomplete record(s) found.")
            st.dataframe(rows, use_container_width=True)
    except Exception as e:
        st.error(f"Error: {e}")
