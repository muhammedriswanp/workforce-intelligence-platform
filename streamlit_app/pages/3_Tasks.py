import streamlit as st
from api_client import api_get, api_post

st.title("Tasks")

# Get project list to populate the dropdown
proj_res = api_get("/projects/")
projects = proj_res.json() if proj_res.status_code == 200 else []
project_options = {p["title"]: p["id"] for p in projects}

# 1. Create Task Form
st.subheader("Add Task to Project")
if project_options:
    with st.form("task_form"):
        selected_project_name = st.selectbox("Assign to Project", options=list(project_options.keys()))
        task_title = st.text_input("Task Title")
        task_desc = st.text_area("Task Description")
        est_hours = st.number_input("Estimated Hours", min_value=1.0, max_value=160.0, value=20.0)
        task_status = st.selectbox("Status", ["todo", "in_progress", "completed"])

        submitted = st.form_submit_button("Save Task")
        if submitted:
            payload = {
                "project_id": project_options[selected_project_name],
                "title": task_title,
                "description": task_desc,
                "estimated_hours": est_hours,
                "status": task_status
            }
            res = api_post("/tasks/", payload)
            if res.status_code in [200, 201]:
                st.success("Task added!")
                st.rerun()
            else:
                st.error(f"Failed to create task: {res.text}")

# 2. View Tasks
st.divider()
st.subheader("All Project Tasks")
task_res = api_get("/tasks/")
if task_res.status_code == 200:
    st.dataframe(task_res.json(), use_container_width=True)