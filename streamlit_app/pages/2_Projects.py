import streamlit as st
from api_client import api_get, api_post

st.title("Projects")

# 1. Create Project Section
st.subheader("Create New Project")
with st.form("create_project"):
    title = st.text_input("Project Title")
    description = st.text_area("Description")
    status = st.selectbox("Status", ["planning", "in_progress", "completed"])
    create_submitted = st.form_submit_button("Create Project")

    if create_submitted:
        payload = {"title": title, "description": description, "status": status}
        res = api_post("/projects/", payload)
        if res.status_code in [200, 201]:
            st.success("Project created!")
            st.rerun()
        else:
            st.error(f"Error: {res.text}")

# 2. List Projects Section
st.divider()
st.subheader("Existing Projects")

