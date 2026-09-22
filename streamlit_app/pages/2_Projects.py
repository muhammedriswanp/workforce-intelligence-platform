import pandas as pd
import streamlit as st
from api_client import api_post, clear_cache, get_projects, get_tasks_for_project
from ui import apply_theme, page_header, kpi, section_title, status_pill, tag
from ui import require_role, render_sidebar, is_manager

st.set_page_config(page_title="Projects", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")

projects = get_projects()
counts = {"planning": 0, "in_progress": 0, "completed": 0}
for p in projects:
    counts[p.get("status", "planning")] = counts.get(p.get("status", "planning"), 0) + 1

page_header("🗂️", "Projects", "Create and manage customer / internal projects")

c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    kpi(len(projects), "Total", icon="🗂️", accent="violet")
with c2:
    kpi(counts["planning"], "Planning", icon="🧭", accent="blue")
with c3:
    kpi(counts["in_progress"], "In progress", icon="⚙️", accent="amber")
with c4:
    kpi(counts["completed"], "Completed", icon="🏁", accent="green")

st.markdown("")

if is_manager():
    section_title("Create a project")
    with st.form("create_project", clear_on_submit=True):
        title = st.text_input("Project title", placeholder="e.g. Customer Analytics Platform")
        description = st.text_area("Description", height=90)
        status = st.selectbox("Status", ["planning", "in_progress", "completed"])
        submitted = st.form_submit_button("Create Project", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Project title is required.")
        else:
            res = api_post(
                "/projects/",
                {"title": title.strip(), "description": description, "status": status},
            )
            if res.status_code in (200, 201):
                clear_cache()
                st.success("Project created.")
                st.rerun()
            else:
                st.error(f"Create failed: {res.text}")
else:
    st.caption("Only managers can create projects.")

st.markdown("")

section_title("All projects")
if not projects:
    st.info("No projects yet. Create one above.")
    st.stop()

for project in projects:
    tasks = get_tasks_for_project(project["id"])
    created = str(project.get("created_at", ""))[:10]
    status = project.get("status", "planning")
    with st.expander(
        f"{project['title']}  ·  {status}  ·  {len(tasks)} tasks",
        expanded=False,
    ):
        st.markdown(
            f"{status_pill(status)} &nbsp; {tag(str(len(tasks)) + ' tasks', 'neutral')}",
            unsafe_allow_html=True,
        )
        if project.get("description"):
            st.markdown(project["description"])
        st.caption(f"Created by user #{project['created_by']} · {created}")
        if tasks:
            task_df = pd.DataFrame(
                [
                    {"ID": t["id"], "Title": t["title"], "Hours": t["estimated_hours"], "Status": t["status"]}
                    for t in tasks
                ]
            )
            st.dataframe(task_df, use_container_width=True, hide_index=True)
        else:
            st.caption("No tasks yet — add some on the Tasks page.")