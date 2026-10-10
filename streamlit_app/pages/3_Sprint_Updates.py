import streamlit as st
from api_client import get_employees, get_employee_assignments, task_lookup
from api_client import create_sprint_update
from ui import apply_theme, render_sidebar, require_role, page_header, section_title

st.set_page_config(page_title="Sprint Updates", layout="wide")
apply_theme()
render_sidebar()
require_role("employee")

employees = get_employees()
my_emp = next(
    (e for e in employees if e.get("user_id") == st.session_state.get("user_id")),
    None,
)

page_header("📝", "Sprint Updates", "Share your progress and blockers on your tasks")

if not my_emp:
    st.info(
        "No employee profile is linked to your account yet. "
        "Ask a manager to link your user account to an employee record on the Employees page."
    )
    st.stop()

emp_id = my_emp["id"]
assignments = get_employee_assignments(emp_id)
active = [a for a in assignments if a.get("status") == "active"]

if not active:
    st.info("You have no active tasks to update yet.")
    st.stop()

tasks_map = task_lookup()
options = {}
for a in active:
    task = tasks_map.get(a["task_id"]) or {}
    title = task.get("title", f"task #{a['task_id']}")
    options[f"#{a['task_id']} · {title}"] = a["task_id"]

section_title("Post an update")

with st.form("sprint_update_form", clear_on_submit=True):
    selected = st.selectbox("Select task", options=list(options.keys()))
    text = st.text_area(
        "Your update",
        height=160,
        placeholder="What did you finish? What are you working on next? Any blockers?",
        max_chars=2000,
    )
    submitted = st.form_submit_button("Post update", type="primary", use_container_width=True)

if submitted:
    clean = (text or "").strip()
    if len(clean) < 3:
        st.warning("Please write at least 3 characters.")
    else:
        task_id = options[selected]
        try:
            with st.spinner("Saving..."):
                res = create_sprint_update(task_id, clean)
        except Exception:
            res = None

        if res is None:
            st.error("Could not save the update. Please try again.")
        elif res.status_code == 201:
            st.success("Update saved.")
        elif res.status_code == 403:
            detail = "You don't have permission to post this update."
            try:
                detail = res.json().get("detail") or detail
            except Exception:
                pass
            st.error(detail)
        elif res.status_code == 422:
            st.error("Update must be between 3 and 2000 characters.")
        else:
            st.error("Could not save the update. Please try again.")

st.markdown("")
st.caption(
    "Your updates are shared with managers and may be used to help recommend people "
    "for future tasks. Do not include personal or sensitive information (health, family, etc.)."
)
