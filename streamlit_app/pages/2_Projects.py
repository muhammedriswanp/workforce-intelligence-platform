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

        st.markdown("")
        st.subheader("🤖 AI Project Decomposition")
        decompose_key = f"proposals_{project['id']}"
        if st.button(
            "Generate Tasks from Documentation",
            use_container_width=True,
            key=f"decompose_{project['id']}",
        ):
            if not (project.get("description") or "").strip():
                st.error("Add a project description/documentation first.")
            else:
                with st.spinner("AI is analyzing document and breaking into tasks..."):
                    response = api_post(f"/projects/{project['id']}/decompose", {})
                if response.status_code == 200:
                    st.session_state[decompose_key] = response.json()
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except Exception:
                        detail = response.text
                    st.error(f"Failed to generate task breakdown: {detail}")

        proposals = st.session_state.get(decompose_key)
        if proposals:
            col_batch, _ = st.columns([2, 3])
            with col_batch:
                if st.button(
                    "Approve & Save Task Plan",
                    key=f"batch_approve_{project['id']}",
                    use_container_width=True,
                ):
                    res = api_post(
                        f"/projects/{project['id']}/tasks/approve-all",
                        {"tasks": proposals},
                    )
                    if res.status_code == 201:
                        st.success("All tasks approved and created!")
                        st.session_state.pop(decompose_key, None)
                        clear_cache()
                        st.rerun()
                    else:
                        st.error(f"Failed to approve tasks: {res.text}")
            st.write(f"### Proposed Tasks ({len(proposals)})")
            for idx, prop in enumerate(proposals):
                with st.container(border=True):
                    st.markdown(f"**Task {idx + 1}: {prop.get('title', '—')}**")
                    st.write(prop.get("description", "") or "")
                    skills = prop.get("required_skills") or []
                    st.caption(
                        f"Estimated: {prop.get('estimated_hours', '—')} hrs | "
                        f"Skills: {', '.join(skills) or '—'}"
                    )
                    act_col, dsc_col = st.columns([2, 1])
                    with act_col:
                        if st.button(
                            f"Approve & Create Task #{idx + 1}",
                            key=f"approve_prop_{project['id']}_{idx}",
                            use_container_width=True,
                        ):
                            res = api_post(
                                f"/projects/{project['id']}/tasks/approve-proposal",
                                prop,
                            )
                            if res.status_code == 201:
                                st.success(f"Task '{prop.get('title', '')}' created in database!")
                                proposals.pop(idx)
                                if proposals:
                                    st.session_state[decompose_key] = proposals
                                else:
                                    st.session_state.pop(decompose_key, None)
                                clear_cache()
                                st.rerun()
                            else:
                                try:
                                    detail = res.json().get("detail", res.text)
                                except Exception:
                                    detail = res.text
                                st.error(f"Approval failed: {detail}")
                    with dsc_col:
                        if st.button(
                            "Discard",
                            key=f"discard_prop_{project['id']}_{idx}",
                            use_container_width=True,
                        ):
                            proposals.pop(idx)
                            if proposals:
                                st.session_state[decompose_key] = proposals
                            else:
                                st.session_state.pop(decompose_key, None)
                            st.rerun()