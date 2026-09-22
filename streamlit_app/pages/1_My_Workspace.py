import pandas as pd
import streamlit as st
from api_client import get_employees, get_workload, get_availability
from api_client import get_employee_skills, get_employee_assignments
from api_client import task_lookup, get_projects
from ui import apply_theme, page_header, kpi, section_title, tag
from ui import require_role, render_sidebar

st.set_page_config(page_title="My Workspace", layout="wide")
apply_theme()
render_sidebar()
require_role("employee")

employees = get_employees()
my_emp = next(
    (e for e in employees if e.get("user_id") == st.session_state.get("user_id")),
    None,
)

page_header("🏠", "My Workspace", "Your profile, workload and assignments")

if not my_emp:
    st.info(
        "No employee profile is linked to your account yet. "
        "Ask a manager to link your user account to an employee record on the Employees page."
    )
else:
    emp_id = my_emp["id"]
    wl = get_workload(emp_id)
    av = get_availability(emp_id)

    p1, p2, p3, p4 = st.columns(4, gap="small")
    exp = my_emp["experience_years"]
    exp_label = f"{exp} yr" if exp == 1 else f"{exp} yrs"
    with p1:
        kpi(exp_label, "Experience", icon="🎓", accent="blue")
    with p2:
        kpi(f"{my_emp['weekly_capacity']}h", "Weekly capacity", icon="📅", accent="violet")
    with p3:
        kpi(f"{wl['workload_percentage']}%" if wl else "—", "Workload", icon="⚡", accent="amber")
    with p4:
        kpi(f"{av['available_hours']:.0f}h" if av else "—", "Available", icon="🕐", accent="green")

    if wl:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;margin-top:8px;">'
            f'<span style="font-size:0.8rem;color:#818cf8;white-space:nowrap;">Allocated</span>'
            f'<div class="scorebar" style="flex:1;"><div class="scorebar-fill" style="width:{min(100.0, float(wl["workload_percentage"] or 0)):.0f}%"></div></div>'
            f'<b style="color:#f8fafc;white-space:nowrap;">{wl["total_allocated_hours"]:.0f}h of {wl["weekly_capacity"]:.0f}h</b></div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    side_l, side_r = st.columns(2, gap="large")

    with side_l:
        section_title("My skills")
        emp_skills = get_employee_skills(emp_id)
        if emp_skills:
            col1, col2 = st.columns(2)
            slots = [col1, col2]
            for i, s in enumerate(emp_skills):
                with slots[i % 2]:
                    st.markdown(tag(f"{s['skill_name']}", s["proficiency_level"]), unsafe_allow_html=True)
        else:
            st.caption("No skills recorded yet.")

    with side_r:
        section_title("My details")
        st.markdown(
            f'<div class="card">'
            f"<b>{my_emp.get('name', f'Employee #{emp_id}')}</b> · {my_emp['designation']}"
            f'<div style="color:#94a3b8;margin-top:6px;">{exp_label} experience · '
            f"{my_emp['weekly_capacity']}h weekly capacity</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("")

    section_title("My assignments")
    assignments = get_employee_assignments(emp_id)
    if assignments:
        tasks_map = task_lookup()
        projects_map = {p["id"]: p for p in get_projects()}
        rows = []
        for a in assignments:
            task = tasks_map.get(a["task_id"]) or {}
            project = projects_map.get(task.get("project_id")) if task.get("project_id") else None
            rows.append(
                {
                    "ID": a["id"],
                    "Task": task.get("title", f"task #{a['task_id']}"),
                    "Project": project.get("title", "—") if project else "—",
                    "Hours": a["allocated_hours"],
                    "Status": a["status"],
                    "Assigned": str(a.get("assigned_at", ""))[:10],
                }
            )
        st.dataframe(
            pd.DataFrame(rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Status": st.column_config.TextColumn("Status", width="medium"),
            },
        )
    else:
        st.caption("You have no assignments yet.")