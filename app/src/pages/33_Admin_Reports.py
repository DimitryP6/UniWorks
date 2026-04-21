import streamlit as st
import requests

API_BASE = "http://api:4000/admin"

st.set_page_config(page_title="Admin Management", layout="wide")
st.title("Admin Management")
st.write("View and manage admin accounts, roles, and access.")

# ------------------------------------------------------------
# Fetch and display all admins
# ------------------------------------------------------------
try:
    response = requests.get(f"{API_BASE}/user")
    admins = response.json()

    if not admins:
        st.info("No admin accounts found.")
    else:
        st.subheader(f"{len(admins)} admin(s)")
        st.dataframe(
            admins,
            use_container_width=True,
            column_order=["admin_id", "full_name", "email", "role", "has_access", "last_login"],
        )
except Exception as e:
    st.error(f"Could not load admins: {e}")

st.divider()

# ------------------------------------------------------------
# Update admin role or access
# ------------------------------------------------------------
st.subheader("Update Admin Role or Access")

admin_id_input = st.number_input("Admin ID to update", min_value=1, step=1)

if st.button("Load Admin"):
    try:
        res = requests.get(f"{API_BASE}/admin/1{int(admin_id_input)}")
        if res.status_code == 404:
            st.warning("Admin not found.")
        else:
            st.session_state["loaded_admin"] = res.json()
    except Exception as e:
        st.error(f"Error: {e}")

if "loaded_admin" in st.session_state:
    a = st.session_state["loaded_admin"]
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

    if st.button("Save Changes", type="primary"):
        payload = {"role": new_role, "has_access": new_access}
        try:
            res = requests.put(f"{API_BASE}/admin/{int(admin_id_input)}", json=payload)
            st.success(res.json().get("message", "Admin updated."))
            del st.session_state["loaded_admin"]
        except Exception as e:
            st.error(f"Error: {e}")

st.divider()

# ------------------------------------------------------------
# Create a new admin
# ------------------------------------------------------------
st.subheader("Create New Admin")

with st.form("new_admin_form"):
    new_user_id   = st.number_input("User ID to promote", min_value=1, step=1)
    new_role      = st.text_input("Role", placeholder="e.g. System Administrator")
    new_has_access = st.selectbox("Has Access", [1, 0],
                                   format_func=lambda x: "Yes" if x == 1 else "No")
    submitted = st.form_submit_button("Create Admin")

if submitted:
    st.warning("Creating new admins is not supported yet.")
