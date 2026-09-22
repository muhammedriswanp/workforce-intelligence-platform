import pandas as pd
import streamlit as st
from api_client import get_projects, get_tasks_for_project, get_task_dependencies
from ui import apply_theme, page_header, kpi, section_title
from ui import require_role, render_sidebar

st.set_page_config(page_title="View Tasks", layout="wide")
apply_theme()
render_sidebar()
require_role("employee")

page_header("✅", "View Tasks", "Browse projects and tasks (read-only)")

projects = get_projects()
project_options = {f"#{p['id']} · {p['title']}": p["id"] for p in projects}
selected = st.selectbox("Select project", options=list(project_options.keys()))
project_id = project_options[selected]
project = next(p for p in projects if p["id"] == project_id)

tasks = get_tasks_for_project(project_id)
total_hours = sum(t.get("estimated_hours", 0) for t in tasks)

p1, p2, p3 = st.columns(3, gap="small")
with p1:
    kpi(f"{project['status']}".title(), "Project", icon="🗂️", accent="blue")
with p2:
    kpi(len(tasks), "Tasks", icon="📋", accent="violet")
with p3:
    kpi(f"{total_hours:.0f}h", "Estimated", icon="🕒", accent="amber")

if project.get("description"):
    st.markdown(project["description"])

st.markdown("")

section_title("Tasks")
if tasks:
    task_map = {t["id"]: t.get("title", f"task #{t['id']}") for t in tasks}

    def deps_labels(task_id):
        deps = get_task_dependencies(task_id)
        if not deps:
            return "—"
        prereq_ids = [
            d["prerequisite_task_id"] if isinstance(d, dict) else d for d in deps
        ]
        return ", ".join(
            str(task_map.get(pid, f"task #{pid}")) for pid in prereq_ids
        )

    rows = [
        {
            "ID": t["id"],
            "Title": t["title"],
            "Est. hours": t["estimated_hours"],
            "Status": t["status"],
            "Depends on": deps_labels(t["id"]),
        }
        for t in tasks
    ]
    st.dataframe(
        pd.DataFrame(rows),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Status": st.column_config.TextColumn("Status", width="medium"),
            "Depends on": st.column_config.TextColumn("Depends on", width="medium"),
        },
    )
else:
    st.caption("No tasks in this project yet.")

st.markdown("")

section_title("About this view")
st.caption(
    "This is a read-only explorer for employees. Managers can create projects, add tasks, "
    "match candidates and approve assignments from the manager pages."
)