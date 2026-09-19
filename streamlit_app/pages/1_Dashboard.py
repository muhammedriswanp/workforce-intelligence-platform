import streamlit as st
from api_client import api_get

st.set_page_config(page_title="Overview Dashboard", layout="wide")
st.title("Workforce Overview Dashboard")

# Fetch data from FastAPI backend
emp_res = api_get("/employees/")
proj_res = api_get("/projects/")

if emp_res.status_code == 200 and proj_res.status_code == 200:
    employees = emp_res.json()
    projects = proj_res.json()

    # Top metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees", len(employees))
    col2.metric("Total Projects", len(projects))
    
    # Calculate average utilization
    total_capacity = sum(e.get("weekly_capacity", 40) for e in employees)
    total_workload = sum(e.get("current_workload", 0) for e in employees)
    utilization = (total_workload / total_capacity * 100) if total_capacity > 0 else 0
    col3.metric("Workforce Allocation", f"{utilization:.1f}%")

    st.divider()

    # Employee Capacity Table
    st.subheader("Employee Workload Status")
    if employees:
        display_data = [
            {
                "Employee ID": emp["id"],
                "User ID": emp["user_id"],
                "Designation": emp["designation"],
                "Experience (Years)": emp["experience_years"],
                "Weekly Capacity (hrs)": emp["weekly_capacity"],
                "Current Workload (hrs)": emp["current_workload"],
            }
            for emp in employees
        ]
        st.dataframe(display_data, use_container_width=True)
    else:
        st.info("No employee records found.")

else:
    st.error("Could not fetch dashboard metrics. Please log in first via the home page.")