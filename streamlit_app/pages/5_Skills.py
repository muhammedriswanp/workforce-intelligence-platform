import pandas as pd
import streamlit as st
from api_client import api_post, clear_cache, get_skills, get_employees, get_employee_skills
from ui import apply_theme, page_header, kpi, section_title, tag, display_name
from ui import require_role, render_sidebar, is_manager

st.set_page_config(page_title="Skills", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")

skills = get_skills()
employees = get_employees()

page_header("🧠", "Skills", "The skill catalogue used for candidate matching")

with st.expander("ℹ️ About skills"):
    st.markdown(
        "Skills are the backbone of candidate matching. When a manager runs candidate matching "
        "on a task, each employee's proficiency (Beginner 50%, Intermediate 75%, Advanced 100%) "
        "feeds the **40% skill weight** of the final score."
    )

st.markdown("")

if is_manager():
    section_title("Add a skill")
    with st.form("create_skill", clear_on_submit=True):
        name = st.text_input("Skill name", placeholder="e.g. PostgreSQL")
        submitted = st.form_submit_button("Add Skill", use_container_width=True)
    if submitted:
        if not name.strip():
            st.error("Skill name is required.")
        else:
            res = api_post("/skills/", {"name": name.strip()})
            if res.status_code in (200, 201):
                clear_cache()
                st.success("Skill added.")
                st.rerun()
            else:
                st.error(f"Create failed: {res.text}")
else:
    st.caption("Only managers can add skills.")

st.markdown("")

c1, c2 = st.columns(2, gap="small")
with c1:
    kpi(len(skills), "Skills", sub="in catalogue", icon="🧠", accent="violet")
with c2:
    assigned = sum(1 for e in employees if get_employee_skills(e["id"]))
    kpi(assigned, "Employees with skills", sub=f"of {len(employees)} profiles", icon="🎯", accent="green")

st.markdown("")

section_title("Skill catalogue")
if not skills:
    st.info("No skills yet. Add some above.")
    st.stop()

for i in range(0, len(skills), 5):
    cols = st.columns(5)
    for j, skill in enumerate(skills[i : i + 5]):
        with cols[j]:
            st.markdown(tag(skill["name"], "neutral"), unsafe_allow_html=True)
            st.caption(f"Skill #{skill['id']}")

st.markdown("")

section_title("Skills held by employees")
if employees:
    employee_options = {f"#{e['id']} · {display_name(e)}": e["id"] for e in employees}
    selected = st.selectbox("Employee", options=list(employee_options.keys()))
    emp_id = employee_options[selected]
    emp_skills = get_employee_skills(emp_id)
    if emp_skills:
        for s in emp_skills:
            st.markdown(tag(f"{s['skill_name']} — {s['proficiency_level']}", s["proficiency_level"]), unsafe_allow_html=True)
    else:
        st.caption("No skills assigned to this employee.")
else:
    st.info("No employee profiles yet.")