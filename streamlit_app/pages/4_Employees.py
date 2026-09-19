import streamlit as st
from api_client import api_get, api_post

st.set_page_config(page_title="Employees", layout="wide")
st.title("Employee Management")

# Fetch master skills for assignment dropdown
skills_res = api_get("/skills/")
skills = skills_res.json() if skills_res.status_code == 200 else []
skill_options = {s["name"]: s["id"] for s in skills}

# 1. Create Employee Profile Form
st.subheader("Create Employee Profile")
with st.form("create_employee_form"):
    user_id = st.number_input("User ID", min_value=1, step=1)
    designation = st.text_input("Designation", placeholder="e.g. Backend Developer")
    experience_years = st.number_input("Experience (Years)", min_value=0.0, step=0.5, value=2.0)
    weekly_capacity = st.number_input("Weekly Capacity (Hours)", min_value=1.0, max_value=80.0, value=40.0)
    submit_emp = st.form_submit_button("Create Profile")

    if submit_emp:
        payload = {
            "user_id": int(user_id),
            "designation": designation,
            "experience_years": experience_years,
            "weekly_capacity": weekly_capacity,
        }
        res = api_post("/employees/", payload)
        if res.status_code in [200, 201]:
            st.success("Employee profile created successfully!")
            st.rerun()
        else:
            st.error(f"Failed to create profile: {res.text}")

st.divider()

# Fetch current employees for viewing and skill assignment
emp_res = api_get("/employees/")
employees = emp_res.json() if emp_res.status_code == 200 else []
employee_options = {f"ID {e['id']} - {e['designation']}": e["id"] for e in employees}

# 2. Assign Skill to Employee Form
st.subheader("Assign Skill to Employee")
if employee_options and skill_options:
    with st.form("assign_skill_form"):
        selected_emp_label = st.selectbox("Select Employee", options=list(employee_options.keys()))
        selected_skill_name = st.selectbox("Select Skill", options=list(skill_options.keys()))
        proficiency = st.selectbox("Proficiency Level", ["Beginner", "Intermediate", "Advanced"])
        submit_skill = st.form_submit_button("Assign Skill")

        if submit_skill:
            emp_id = employee_options[selected_emp_label]
            skill_id = skill_options[selected_skill_name]
            payload = {
                "skill_id": skill_id,
                "proficiency_level": proficiency,
            }
            res = api_post(f"/employees/{emp_id}/skills", payload)
            if res.status_code in [200, 201]:
                st.success("Skill assigned successfully!")
                st.rerun()
            else:
                st.error(f"Failed to assign skill: {res.text}")
elif not employee_options:
    st.info("Create an employee profile first to assign skills.")
elif not skill_options:
    st.info("No skills available. Add skills via the backend or API first.")

st.divider()

# 3. View All Employees
st.subheader("All Employees")
if employees:
    st.dataframe(employees, use_container_width=True)
else:
    st.info("No employees found.")