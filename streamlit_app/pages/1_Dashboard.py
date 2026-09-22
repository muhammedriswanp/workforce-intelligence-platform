import pandas as pd
import streamlit as st
from api_client import get_employees, get_projects, get_assignments
from api_client import get_all_tasks, get_workload, get_availability, get_employee_skills
from ui import apply_theme, page_header, kpi, section_title, status_pill, display_name
from ui import require_role, render_sidebar, alert_markup

st.set_page_config(page_title="Dashboard", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")

employees = get_employees()
projects = get_projects()
tasks = get_all_tasks()
assignments = get_assignments()

total_capacity = sum(e.get("weekly_capacity", 40) for e in employees)
total_allocated = sum(e.get("current_workload", 0) for e in employees)
utilization = round((total_allocated / total_capacity) * 100, 1) if total_capacity > 0 else 0

page_header("📊", "Overview dashboard", "Live workforce and project intelligence")

c1, c2, c3, c4, c5 = st.columns(5, gap="small")
with c1:
    kpi(len(employees), "Employees", icon="🧑‍💼", accent="blue")
with c2:
    kpi(len(projects), "Projects", icon="🗂️", accent="violet")
with c3:
    kpi(len(tasks), "Tasks", icon="✅", accent="indigo")
with c4:
    kpi(len(assignments), "Assignments", icon="📌", accent="amber")
with c5:
    kpi(f"{utilization}%", "Allocated", sub="of weekly capacity", icon="⚡", accent="green")

st.markdown("")

col_work, col_proj = st.columns(2, gap="large")

with col_work:
    section_title("Workload by employee")
    if employees:
        rows = []
        for e in employees:
            wl = get_workload(e["id"])
            rows.append(
                {
                    "employee": f"#{e['id']} {display_name(e)}",
                    "workload": round(wl["workload_percentage"], 1) if wl else 0,
                }
            )
        chart = pd.DataFrame(rows).sort_values("workload", ascending=False)
        st.bar_chart(chart.set_index("employee"), color="#6366f1")
    else:
        st.info("No employee profiles yet.")

with col_proj:
    section_title("Project pipeline")
    if projects:
        counts = {"planning": 0, "in_progress": 0, "completed": 0}
        for p in projects:
            key = p.get("status", "planning")
            counts[key] = counts.get(key, 0) + 1
        chart_data = pd.DataFrame(
            {"status": list(counts.keys()), "count": list(counts.values())}
        )
        st.bar_chart(chart_data.set_index("status"), color="#10b981")
    else:
        st.info("No projects yet.")

st.markdown("")

section_title("Utilization alerts")
alerts = []
for e in employees:
    wl = get_workload(e["id"])
    if not wl:
        continue
    status = wl.get("status")
    if status == "overloaded":
        alerts.append(("danger", f"🛑", f"#{e['id']} {display_name(e)} is overloaded at {wl['workload_percentage']}%"))
    elif status == "optimal":
        alerts.append(("warn", "⚠️", f"#{e['id']} {display_name(e)} is optimally loaded at {wl['workload_percentage']}%"))
if not alerts and employees:
    st.success("Everyone is comfortably under capacity right now.")

for kind, icon, text in alerts[:6]:
    alert_markup(icon, text, kind)

st.markdown("")

section_title("Employee utilization table")
if employees:
    rows = []
    for e in employees:
        wl = get_workload(e["id"])
        av = get_availability(e["id"])
        skill_count = len(get_employee_skills(e["id"]))
        rows.append(
            {
                "ID": e["id"],
                "Name": display_name(e),
                "Designation": e["designation"],
                "Experience": e["experience_years"],
                "Capacity": e["weekly_capacity"],
                "Allocated hrs": round(wl["total_allocated_hours"], 1) if wl else 0,
                "Workload %": round(wl["workload_percentage"], 1) if wl else 0,
                "Available hrs": round(av["available_hours"], 1) if av else e["weekly_capacity"],
                "Status": (wl or {}).get("status", "unknown"),
                "Skills": skill_count,
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Workload %": st.column_config.ProgressColumn(
                "Workload %",
                min_value=0,
                max_value=int(df["Workload %"].max() or 100) + 20,
                format="%.0f%%",
            )
        },
    )
else:
    st.info("No employee profiles yet. Create one on the Employees page.")