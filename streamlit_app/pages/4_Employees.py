import pandas as pd
import streamlit as st
from api_client import api_post, clear_cache, get_employees, get_skills, get_users
from api_client import get_workload, get_availability, get_employee_skills
from ui import apply_theme, page_header, kpi, section_title, status_pill, tag, display_name
from ui import require_role, render_sidebar, is_manager

st.set_page_config(page_title="Employees", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")

employees = get_employees()

page_header("🧑‍💼", "Employees", "Profiles, skills, workload and availability")

counts = {"underloaded": 0, "optimal": 0, "overloaded": 0}
status_details = {}
for e in employees:
    wl = get_workload(e["id"])
    status = (wl or {}).get("status", "unknown")
    counts[status] = counts.get(status, 0) + 1
    status_details[e["id"]] = wl

c1, c2, c3, c4 = st.columns(4, gap="small")
with c1:
    kpi(len(employees), "Total", icon="🧑‍💼", accent="blue")
with c2:
    kpi(counts["underloaded"], "Underloaded", sub="headroom available", icon="🟢", accent="green")
with c3:
    kpi(counts["optimal"], "Optimal", sub="70–100% loaded", icon="🟠", accent="amber")
with c4:
    kpi(counts["overloaded"], "Overloaded", sub="over capacity", icon="🔴", accent="rose")

st.markdown("")

if is_manager():
    section_title("Create employee profile")
    users = get_users()
    assigned_user_ids = {e["user_id"] for e in employees}
    available_users = [u for u in users if u["id"] not in assigned_user_ids]
    if not available_users:
        st.caption("Every registered user already has an employee profile.")
    else:
        user_options = {
            f"{u['name']} · {u['email']} · {u['role']}": u["id"] for u in available_users
        }
        with st.form("create_employee", clear_on_submit=True):
            selected_user = st.selectbox("User", options=list(user_options.keys()))
            designation = st.text_input("Designation", placeholder="e.g. Backend Developer")
            experience_years = st.number_input("Experience (years)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
            weekly_capacity = st.number_input("Weekly capacity (hours)", min_value=1.0, max_value=80.0, value=40.0)
            submitted = st.form_submit_button("Create Profile", use_container_width=True)

        if submitted:
            if not designation.strip():
                st.error("Designation is required.")
            else:
                res = api_post(
                    "/employees/",
                    {
                        "user_id": int(user_options[selected_user]),
                        "designation": designation.strip(),
                        "experience_years": int(experience_years),
                        "weekly_capacity": weekly_capacity,
                    },
                )
                if res.status_code in (200, 201):
                    clear_cache()
                    st.success("Employee profile created.")
                    st.rerun()
                else:
                    st.error(f"Create failed: {res.text}")
else:
    st.caption("Only managers can create employee profiles or assign skills.")

st.markdown("")

if not employees:
    st.info("No employee profiles yet.")
    st.stop()

section_title("Employee spotlight")
options = {f"#{e['id']} · {display_name(e)}": e["id"] for e in employees}
selected = st.selectbox("Select employee", options=list(options.keys()))
emp_id = options[selected]
employee = next(e for e in employees if e["id"] == emp_id)

wl = get_workload(emp_id)
av = get_availability(emp_id)

p1, p2, p3, p4 = st.columns(4, gap="small")
exp = employee["experience_years"]
exp_label = f"{exp} yr" if exp == 1 else f"{exp} yrs"
with p1:
    kpi(exp_label, "Experience", icon="🎓", accent="blue")
with p2:
    kpi(f"{employee['weekly_capacity']}h", "Weekly capacity", icon="📅", accent="violet")
with p3:
    kpi(f"{wl['workload_percentage']}%" if wl else "—", "Workload", icon="⚡", accent="amber")
with p4:
    kpi(f"{av['available_hours']:.0f}h" if av else "—", "Available", icon="🕐", accent="green")

if wl:
    st.progress(min(1.0, wl["workload_percentage"] / 100))
    st.caption(
        f"Allocated {wl['total_allocated_hours']:.0f}h of {wl['weekly_capacity']:.0f}h · {status_pill(wl['status'])}"
    )

st.markdown("")

side_l, side_r = st.columns(2, gap="large")

with side_l:
    section_title("Skills")
    emp_skills = get_employee_skills(emp_id)
    if emp_skills:
        col1, col2 = st.columns(2)
        slots = [col1, col2]
        for i, s in enumerate(emp_skills):
            with slots[i % 2]:
                st.markdown(tag(f"{s['skill_name']}", s["proficiency_level"]), unsafe_allow_html=True)
                st.caption(s["proficiency_level"])
    else:
        st.caption("No skills assigned yet.")

with side_r:
    if is_manager():
        skills = get_skills()
        if skills:
            section_title("Assign a skill")
            skill_options = {s["name"]: s["id"] for s in skills}
            with st.form("assign_skill", clear_on_submit=True):
                skill_name = st.selectbox("Skill", options=list(skill_options.keys()))
                proficiency = st.selectbox("Proficiency", ["Beginner", "Intermediate", "Advanced"])
                submitted = st.form_submit_button("Assign", use_container_width=True)
            if submitted:
                res = api_post(
                    f"/employees/{emp_id}/skills",
                    {"skill_id": skill_options[skill_name], "proficiency_level": proficiency},
                )
                if res.status_code in (200, 201):
                    clear_cache()
                    st.success("Skill assigned.")
                    st.rerun()
                else:
                    st.error(f"Assign failed: {res.text}")

st.markdown("")

section_title("All employees")
rows = []
for e in employees:
    e_wl = get_workload(e["id"])
    skill_count = len(get_employee_skills(e["id"]))
    rows.append(
        {
            "ID": e["id"],
            "Name": display_name(e),
            "Designation": e["designation"],
            "Experience": e["experience_years"],
            "Capacity": e["weekly_capacity"],
            "Workload %": round(e_wl["workload_percentage"], 1) if e_wl else 0,
            "Status": (e_wl or {}).get("status", "unknown"),
            "Skills": skill_count,
        }
    )
df = pd.DataFrame(rows).sort_values("Workload %", ascending=False)
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