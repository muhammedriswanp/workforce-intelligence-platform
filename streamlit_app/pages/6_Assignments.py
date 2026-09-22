import pandas as pd
import streamlit as st
from api_client import get_assignments, get_employee_assignments, get_employees
from api_client import get_all_tasks, task_lookup, get_projects
from ui import apply_theme, page_header, kpi, section_title, status_pill, display_name
from ui import require_role, render_sidebar

st.set_page_config(page_title="Assignments", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")

employees = get_employees()
employee_options = {"All employees": None}
employee_options.update({f"#{e['id']} · {display_name(e)}": e["id"] for e in employees})

page_header("📌", "Assignments", "Who is working on what")

scope = st.selectbox("Filter", options=list(employee_options.keys()))
selected_emp_id = employee_options[scope]

assignments = get_employee_assignments(selected_emp_id) if selected_emp_id else get_assignments()

tasks_map = task_lookup()
projects_map = {p["id"]: p for p in get_projects()}
employee_map = {e["id"]: e for e in employees}

rows = []
for a in assignments:
    task = tasks_map.get(a["task_id"]) or {}
    project = projects_map.get(task.get("project_id")) if task.get("project_id") else None
    employee = employee_map.get(a["employee_id"]) or {}
    rows.append(
        {
            "ID": a["id"],
            "Task": task.get("title", f"task #{a['task_id']}"),
            "Project": project.get("title", "—") if project else "—",
            "Employee": display_name(employee, f"emp #{a['employee_id']}"),
            "Hours": a["allocated_hours"],
            "Status": a["status"],
            "Assigned": str(a.get("assigned_at", ""))[:10],
        }
    )

active = sum(1 for a in assignments if a.get("status") == "active")
completed = sum(1 for a in assignments if a.get("status") == "completed")
committed_hours = sum(a.get("allocated_hours", 0) for a in assignments if a.get("status") == "active")

c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    kpi(len(assignments), "Assignments", icon="📌", accent="violet")
with c2:
    kpi(active, "Active", icon="⚙️", accent="amber")
with c3:
    kpi(completed, "Completed", icon="🏁", accent="green")
with c4:
    kpi(f"{committed_hours:.0f}h", "Committed", sub="active workload", icon="⚡", accent="indigo")

st.markdown("")

section_title("Assignment log")
if not rows:
    st.info("No assignments found for this filter.")
    st.stop()

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)

status_summary = df["Status"].value_counts().to_dict()
if status_summary:
    st.markdown("")
    section_title("Status breakdown")
    summary_df = pd.DataFrame({"Status": list(status_summary.keys()), "Count": list(status_summary.values())})
    st.bar_chart(summary_df.set_index("Status"), color="#6366f1")