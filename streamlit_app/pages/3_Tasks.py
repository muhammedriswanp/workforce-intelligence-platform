import pandas as pd
import streamlit as st
from api_client import api_post, clear_cache, get_projects, get_tasks_for_project
from api_client import get_task_candidates, get_task_dependencies, get_assignments
from ui import apply_theme, page_header, kpi, section_title, status_pill, score_bar, display_name
from ui import require_role, render_sidebar, is_manager

st.set_page_config(page_title="Tasks", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")

projects = get_projects()
project_options = {p["title"]: p["id"] for p in projects}

page_header("✅", "Tasks", "Create tasks, match candidates, and approve assignments")

if not projects:
    st.info("Create a project first before adding tasks.")
    st.stop()

selected_project = st.selectbox("Project", options=list(project_options.keys()), key="task_project")
project_id = project_options[selected_project]
tasks = get_tasks_for_project(project_id)
task_options = {f"#{t['id']} · {t['title']}": t["id"] for t in tasks}

c1, c2, c3 = st.columns(3, gap="small")
total_hours = sum(t.get("estimated_hours", 0) for t in tasks)
with c1:
    kpi(len(tasks), "Tasks", sub=selected_project, icon="✅", accent="indigo")
with c2:
    kpi(total_hours, "Est. hours", sub="in this project", icon="⏱️", accent="amber")
with c3:
    kpi(sum(1 for t in tasks if t.get("status") == "completed"), "Completed", icon="🏁", accent="green")

st.markdown("")

if is_manager():
    section_title("Add a task")
    with st.form("create_task", clear_on_submit=True):
        title = st.text_input("Task title", placeholder="e.g. Build API")
        description = st.text_area("Description", height=70)
        estimated_hours = st.number_input("Estimated hours", min_value=1.0, max_value=160.0, value=20.0)
        status = st.selectbox("Status", ["todo", "in_progress", "completed"])
        submitted = st.form_submit_button("Add Task", use_container_width=True)

    if submitted:
        if not title.strip():
            st.error("Task title is required.")
        else:
            res = api_post(
                "/tasks/",
                {
                    "project_id": project_id,
                    "title": title.strip(),
                    "description": description,
                    "estimated_hours": estimated_hours,
                    "status": status,
                },
            )
            if res.status_code in (200, 201):
                clear_cache()
                st.success("Task added.")
                st.rerun()
            else:
                st.error(f"Create failed: {res.text}")
else:
    st.caption("Only managers can create tasks, match candidates, or approve assignments.")

st.markdown("")

section_title("Task list")
if not tasks:
    st.info("No tasks in this project yet.")
    st.stop()

task_df = pd.DataFrame(
    [
        {
            "ID": t["id"],
            "Title": t["title"],
            "Est. hours": t["estimated_hours"],
            "Status": t["status"],
        }
        for t in tasks
    ]
)
st.dataframe(task_df, use_container_width=True, hide_index=True)

st.markdown("")

section_title("Work with a task")
selected_label = st.selectbox("Select a task", options=list(task_options.keys()))
task_id = task_options[selected_label]
current_task = next(t for t in tasks if t["id"] == task_id)

match_col, dep_col = st.columns([3, 2], gap="large")

with match_col:
    pill = status_pill(current_task.get("status", "todo"))
    st.markdown(f"### {current_task['title']} {pill}", unsafe_allow_html=True)
    if current_task.get("description"):
        st.caption(current_task["description"])
    st.caption(f"Estimated {current_task['estimated_hours']} hours")

    if not is_manager():
        st.caption("Only managers can run candidate matching.")
    else:
        if st.button("🎯 Run candidate matching", type="primary", use_container_width=True, key=f"match_{task_id}"):
            candidates = get_task_candidates(task_id)
            if candidates:
                st.session_state[f"candidates_{task_id}"] = candidates
            else:
                st.session_state[f"candidates_{task_id}"] = []

        candidates = st.session_state.get(f"candidates_{task_id}")
        if candidates:
            candidates = sorted(candidates, key=lambda c: c["final_score"], reverse=True)
            active_assignments = {
                (a["task_id"], a["employee_id"])
                for a in get_assignments()
                if a.get("status") == "active"
            }

            st.caption("Ranking is an AI suggestion — you may review and approve any candidate below.")
            if st.button("🗑️ Clear ranking", use_container_width=True, key=f"clear_ranking_{task_id}"):
                st.session_state[f"candidates_{task_id}"] = None
                st.rerun()
            st.markdown("")

            for rank, cand in enumerate(candidates[:5], start=1):
                c = cand["employee_id"]
                with st.container(border=True):
                    col_a, col_b = st.columns([2, 3])
                    with col_a:
                        st.markdown(f"**#{rank} · {display_name(cand)}**")
                        st.caption(
                            f"{cand.get('designation', 'Employee')} · emp #{cand['employee_id']} · {cand['experience_years']} yrs exp"
                        )
                    with col_b:
                        st.markdown(f"Final score {score_bar(cand['final_score'])}", unsafe_allow_html=True)
                        st.markdown(
                            "&nbsp;&nbsp;".join(
                                [
                                    f"⚡ skills {cand['metrics']['skill_score']:.0f}",
                                    f"🕐 avail {cand['metrics']['availability_score']:.0f}",
                                    f"💪 work {cand['metrics']['workload_score']:.0f}",
                                    f"🎓 exp {cand['metrics']['experience_score']:.0f}",
                                ]
                            ),
                            unsafe_allow_html=True,
                        )

                    if is_manager():
                        if (task_id, c) in active_assignments:
                            st.info("Already actively assigned to this task.")
                        else:
                            est_hours = max(1.0, float(current_task.get("estimated_hours", 40) or 40))
                            act_col, cnfr_col, btn_col = st.columns([2, 2, 1.5])
                            with act_col:
                                hours = st.number_input(
                                    "Hours to allocate",
                                    min_value=1.0,
                                    max_value=est_hours,
                                    value=min(est_hours, 20.0),
                                    step=1.0,
                                    key=f"hours_{task_id}_{c}",
                                )
                            with cnfr_col:
                                confirm = st.checkbox(
                                    f"Confirm {display_name(cand).split()[0] if display_name(cand) else cand}",
                                    key=f"confirm_{task_id}_{c}",
                                )
                            with btn_col:
                                if st.button(
                                    f"✅ Approve #{c}",
                                    key=f"ok_{task_id}_{c}",
                                    disabled=not confirm,
                                    use_container_width=True,
                                ):
                                    res = api_post(
                                        "/assignments/approve",
                                        {
                                            "task_id": task_id,
                                            "employee_id": c,
                                            "allocated_hours": hours,
                                        },
                                    )
                                    if res.status_code in (200, 201):
                                        clear_cache()
                                        st.session_state[f"candidates_{task_id}"] = None
                                        st.success("Assignment approved — workload is now live.")
                                        st.rerun()
                                    else:
                                        try:
                                            detail = res.json().get("detail", res.text)
                                        except Exception:
                                            detail = res.text
                                        st.error(f"Approval failed: {detail}")
        else:
            st.warning("No candidates found. Make sure employees exist with skills.")

with dep_col:
    st.markdown("### 🔗 Dependencies")
    existing = get_task_dependencies(task_id)
    if existing:
        for dep in existing:
            st.markdown(status_pill(f"#{dep['task_id']} requires #{dep['prerequisite_task_id']}"), unsafe_allow_html=True)
    else:
        st.caption("No dependencies defined yet.")

    if is_manager():
        st.markdown("#### Add dependency")
        other_tasks = [t for t in tasks if t["id"] != task_id]
        if other_tasks:
            prereq_label = st.selectbox(
                "Prerequisite (must finish first)",
                options=[f"#{t['id']} · {t['title']}" for t in other_tasks],
                key=f"prereq_{task_id}",
            )
            prereq_id = [t for t in other_tasks if f"#{t['id']} · {t['title']}" == prereq_label][0]["id"]
            if st.button("Add dependency", use_container_width=True, key=f"dep_{task_id}"):
                res = api_post(f"/tasks/{task_id}/dependencies", {"prerequisite_task_id": prereq_id})
                if res.status_code in (200, 201):
                    clear_cache()
                    st.success("Dependency added.")
                    st.rerun()
                else:
                    st.error(f"Failed: {res.text}")
        else:
            st.caption("No other tasks in this project to depend on.")