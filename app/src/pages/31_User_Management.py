import streamlit as st
import requests

API_BASE = "http://api:4000"

st.set_page_config(page_title="User Management", layout="wide")
st.title("User Management")
st.write("View, filter, and manage all platform users.")

if "loaded_seeker" not in st.session_state:
    st.session_state.loaded_seeker = None
if "loaded_admin" not in st.session_state:
    st.session_state.loaded_admin = None

# ------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------
with st.sidebar:
    st.header("Filters")
    user_type_filter = st.selectbox(
        "User Type",
        ["All", "Student", "Job Poster", "Admin"],
    )
    status_filter = st.selectbox("Status", ["All", "Active", "Inactive"])

# ------------------------------------------------------------
# Fetch and display users
# ------------------------------------------------------------
try:
    response = requests.get(f"{API_BASE}/admin/user")
    users = response.json()
 
    # Apply filters (client-side since API doesn't support them)
    if user_type_filter != "All":
        users = [u for u in users if u.get("user_type") == user_type_filter]
    if status_filter == "Active":
        users = [u for u in users if u.get("is_active")]
    elif status_filter == "Inactive":
        users = [u for u in users if not u.get("is_active")]
 
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

if st.button("Archive Inactive Users", type="primary"):
    try:
        res = requests.put(f"{API_BASE}/admin/user")
        data = res.json()
        st.success(f"{data.get('archived_count', 0)} user(s) archived.")
    except Exception as e:
        st.error(f"Error: {e}")
 
st.divider()

# ------------------------------------------------------------
# Edit individual user
# ------------------------------------------------------------
st.subheader("Edit a User Record")
st.write("Update profile fields or fix incomplete records.")

seeker_id_input = st.number_input("Enter Job Seeker ID to edit", min_value=1, step=1, key="seeker_id")
 
if st.button("Load Job Seeker"):
    try:
        res = requests.get(f"{API_BASE}/admin/job_seeker/{int(seeker_id_input)}")
        if res.status_code == 404:
            st.warning("Job seeker not found.")
            st.session_state.loaded_seeker = None
        else:
            st.session_state.loaded_seeker = res.json()
    except Exception as e:
        st.error(f"Error: {e}")
 
if st.session_state.loaded_seeker:
    s = st.session_state.loaded_seeker
    st.write(f"Editing: **{s.get('full_name')}** ({s.get('email')})")
 
    col1, col2 = st.columns(2)
    with col1:
        new_major = st.text_input("Major", value=s.get("major", "") or "")
        new_university = st.text_input("University", value=s.get("university", "") or "")
        new_city = st.text_input("City/State", value=s.get("city_state", "") or "")
    with col2:
        new_phone = st.text_input("Phone Number", value=s.get("phone_number", "") or "")
        degree_options = ["Bachelors", "Masters", "PHD"]
        current_degree = s.get("degree_level", "Bachelors")
        new_degree = st.selectbox(
            "Degree Level",
            degree_options,
            index=degree_options.index(current_degree) if current_degree in degree_options else 0,
        )
 
    if st.button("Save Job Seeker Changes", type="primary"):
        payload = {
            "major": new_major,
            "university": new_university,
            "city_state": new_city,
            "phone_number": new_phone,
            "degree_level": new_degree,
        }
        try:
            res = requests.put(f"{API_BASE}/admin/job_seeker/{int(seeker_id_input)}", json=payload)
            st.success(res.json().get("message", "Profile updated successfully."))
            st.session_state.loaded_seeker = None
        except Exception as e:
            st.error(f"Error: {e}")
 
st.divider()

# ------------------------------------------------------------
# Edit Admin role / access
# ------------------------------------------------------------
st.subheader("Edit Admin Role / Access")
 
admin_id_input = st.number_input("Enter Admin ID to edit", min_value=1, step=1, key="admin_id")
 
if st.button("Load Admin"):
    try:
        res = requests.get(f"{API_BASE}/admin/admin/{int(admin_id_input)}")
        if res.status_code == 404:
            st.warning("Admin not found.")
            st.session_state.loaded_admin = None
        else:
            st.session_state.loaded_admin = res.json()
    except Exception as e:
        st.error(f"Error: {e}")
 
if st.session_state.loaded_admin:
    a = st.session_state.loaded_admin
    st.write(f"Editing: **{a.get('full_name')}** — current role: `{a.get('role')}`")
 
    col1, col2 = st.columns(2)
    with col1:
        new_role = st.text_input("Role", value=a.get("role", ""))
    with col2:
        new_access = st.selectbox(
            "Has Access",
            [1, 0],
            index=0 if a.get("has_access") else 1,
            format_func=lambda x: "Yes" if x == 1 else "No",
        )
 
    if st.button("Save Admin Changes", type="primary"):
        payload = {"role": new_role, "has_access": new_access}
        try:
            res = requests.put(f"{API_BASE}/admin/admin/{int(admin_id_input)}", json=payload)
            st.success(res.json().get("message", "Admin updated."))
            st.session_state.loaded_admin = None
        except Exception as e:
            st.error(f"Error: {e}")
 