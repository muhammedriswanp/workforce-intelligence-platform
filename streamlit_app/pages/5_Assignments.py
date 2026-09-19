import streamlit as st
from api_client import api_get, api_post

st.set_page_config(page_title="Assignments", layout="wide")
st.title("Task Assignments")

# Fetch tasks, employees, and existing assignments
tasks_res = api_get("/tasks/")
emp_res = api_get("/employees/")
assign_res = api_get("/assignments/")

tasks = tasks_res.json() if tasks_res.status_code == 200 else []
employees = emp_res.json() if emp_res.status_code == 200 else []
assignments = assign_res.json() if assign_res.status_code == 200 else []

task_options = {f"Task #{t['id']}: {t['title']} ({t['estimated_hours']} hrs)": t["id"] for t in tasks}
employee_options = {f"Emp #{e['id']}: {e['designation']} (Workload: {e['current_workload']} hrs)": e["id"] for e in employees}

# 1. Manual Assignment Form
st.subheader("Assign Employee to Task")
if task_options and employee_options:
    with st.form("create_assignment_form"):
        selected_task_label = st.selectbox("Select Task", options=list(task_options.keys()))
        selected_emp_label = st.selectbox("Select Employee", options=list(employee_options.keys()))
        allocated_hours = st.number_input("Allocated Hours", min_value=1.0, max_value=80.0, value=20.0, step=1.0)
        
        submit_assignment = st.form_submit_button("Create Assignment")
        if submit_assignment:
            task_id = task_options[selected_task_label]
            emp_id = employee_options[selected_emp_label]
            
            payload = {
                "task_id": task_id,
                "employee_id": emp_id,
                "allocated_hours": allocated_hours,
            }
            res = api_post("/assignments/", payload)
            if res.status_code in [200, 201]:
                st.success("Assignment created and workload updated!")
                st.rerun()
            else:
                st.error(f"Failed to create assignment: {res.text}")
elif not task_options:
    st.info("No tasks available. Create a task first in the Tasks page.")
elif not employee_options:
    st.info("No employees available. Create an employee profile first in the Employees page.")

st.divider()

# 2. View All Active Assignments
st.subheader("Current Assignments")
if assignments:
    st.dataframe(assignments, use_container_width=True)
else:
    st.info("No active assignments recorded.")