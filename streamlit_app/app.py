import streamlit as st
from api_client import login_user, register_user, api_get
from api_client import get_employees, get_projects, get_all_tasks, get_assignments
from api_client import get_employee_skills, get_employee_assignments, get_workload
from ui import apply_theme, hero, kpi, section_title, render_sidebar, status_pill, tag, display_name

st.set_page_config(
    page_title="Workforce Intelligence Platform",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_theme()
render_sidebar()

if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "name" not in st.session_state:
    st.session_state.name = None
if "email" not in st.session_state:
    st.session_state.email = None

if "auth_view" not in st.session_state:
    st.session_state.auth_view = "login"

if not st.session_state.token:
    hero(
        "Workforce Intelligence Platform",
        "AI-powered workforce, skill and workload management",
    )

    st.markdown(
        '<style>'
        ".auth-wrap { max-width: 520px; margin: 0 auto; }"
        ".auth-panel header { display:flex; align-items:center; gap:6px; margin-bottom: 4px; }"
        ".auth-panel .auth-icon { font-size: 1.15rem; }"
        ".auth-panel h2 { margin: 0; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.01em; }"
        ".auth-switch { margin-top: 16px; text-align: center; }"
        ".auth-switch p { color: #94a3b8; font-size: 0.85rem; margin: 0 0 6px; }"
        "</style>",
        unsafe_allow_html=True,
    )

    st.markdown('<div class="auth-wrap">', unsafe_allow_html=True)

    if st.session_state.auth_view == "login":
        st.markdown(
            '<div class="card auth-panel"><div class="card-title">'
            '<span class="auth-icon">🔐</span> &nbsp;Sign in to your account</div>',
            unsafe_allow_html=True,
        )
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@company.com")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

        if submitted:
            if not email or not password:
                st.error("Email and password are required.")
            else:
                res = login_user(email, password)
                if res.status_code == 200:
                    st.session_state.token = res.json()["access_token"]
                    me = api_get("/auth/me")
                    if me.status_code == 200:
                        payload = me.json().get("user", {})
                        st.session_state.user_id = payload.get("user_id")
                        st.session_state.role = payload.get("role")
                        st.session_state.name = payload.get("name")
                        st.session_state.email = payload.get("email")
                    st.success("Login successful. Loading workspace...")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.markdown(
            '<div class="auth-switch"><p>New to the platform?</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("Create an account", use_container_width=True, key="goto_register"):
            st.session_state.auth_view = "register"
            st.rerun()

    else:
        st.markdown(
            '<div class="card auth-panel"><div class="card-title">'
            '<span class="auth-icon">✨</span> &nbsp;Create an account</div>',
            unsafe_allow_html=True,
        )
        with st.form("register_form"):
            name = st.text_input("Full name", placeholder="John Doe")
            reg_email = st.text_input("Email", placeholder="john@company.com")
            reg_password = st.text_input("Password", type="password")
            role = st.selectbox("Role", ["employee", "manager"])
            reg_submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")
        st.markdown("</div>", unsafe_allow_html=True)

        if reg_submitted:
            if not (name and reg_email and reg_password):
                st.error("All fields are required.")
            else:
                res = register_user(name, reg_email, reg_password, role)
                if res.status_code in (200, 201):
                    st.session_state.auth_view = "login"
                    st.success("Account created. Sign in to continue.")
                    st.rerun()
                else:
                    st.error(f"Registration failed: {res.text}")

        st.markdown(
            '<div class="auth-switch"><p>Already have an account?</p></div>',
            unsafe_allow_html=True,
        )
        if st.button("Back to sign in", use_container_width=True, key="goto_login"):
            st.session_state.auth_view = "login"
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

else:
    employees = get_employees()
    projects = get_projects()
    if st.session_state.role == "manager":
        tasks = get_all_tasks()
        assignments = get_assignments()
    else:
        tasks, assignments = [], []

    role_display = str(st.session_state.role or "user").title()
    signed_in_as = st.session_state.get("name") or f"User #{st.session_state.get('user_id')}"
    hero(
        "Workforce Intelligence Platform",
        f"Signed in as {signed_in_as} · {role_display}",
    )

    if st.session_state.role != "manager":
        my_emp = next(
            (e for e in employees if e.get("user_id") == st.session_state.get("user_id")),
            None,
        )
        section_title("My workspace")
        if my_emp:
            wl = get_workload(my_emp["id"])
            c1, c2, c3, c4 = st.columns(4, gap="small")
            with c1:
                kpi(display_name(my_emp), "Employee", sub=my_emp.get("designation") or "Staff", icon="🧑‍💼", accent="blue")
            with c2:
                kpi(f"{my_emp.get('experience_years', 0):.1f}y", "Experience", icon="📈", accent="violet")
            with c3:
                kpi(f"{wl['total_allocated_hours']:.0f}h" if wl else "—", "Allocated", sub=f"of {my_emp.get('weekly_capacity', 40):.0f}h weekly", icon="⚡", accent="amber")
            with c4:
                kpi(len(get_employee_assignments(my_emp["id"])), "Assignments", icon="📌", accent="green")
            st.markdown("")
            if wl:
                progress = wl.get("workload_percentage") or (wl["total_allocated_hours"] / my_emp["weekly_capacity"] * 100 if my_emp["weekly_capacity"] else 0)
                st.markdown(
                    f'<div style="display:flex;align-items:center;gap:10px;margin-top:8px;">'
                    f'<span style="font-size:0.8rem;color:#818cf8;white-space:nowrap;">Workload</span>'
                    f'<div class="scorebar" style="flex:1;"><div class="scorebar-fill" style="width:{min(100.0, float(progress)):.0f}%"></div></div>'
                    f'<b style="color:#f8fafc;white-space:nowrap;">{status_pill(wl["status"])}</b></div>',
                    unsafe_allow_html=True,
                )
            skills = get_employee_skills(my_emp["id"])
            if skills:
                st.markdown("")
                section_title("My skills")
                names = [s.get("name") or s.get("skill_name") for s in skills]
                st.markdown(" ".join(tag(n) for n in names), unsafe_allow_html=True)

            st.markdown("")
            section_title("Quick actions")
            q1, q2 = st.columns(2, gap="small")
            with q1:
                st.page_link("pages/1_My_Workspace.py", label="🏠 &nbsp; My workspace", use_container_width=True)
            with q2:
                st.page_link("pages/2_View_Tasks.py", label="✅ &nbsp; View tasks", use_container_width=True)

            st.markdown("")
            section_title("What you can do")
            st.markdown(
                '<div class="steps">'
                "<div class='step'><div class='step-num'>Track</div><div class='step-title'>Your workload</div>"
                "<div class='step-desc'>See allocated hours, availability and your current status at a glance.</div></div>"
                "<div class='step'><div class='step-num'>Review</div><div class='step-title'>Your assignments</div>"
                "<div class='step-desc'>Every task you are assigned, with hours and approval status.</div></div>"
                "<div class='step'><div class='step-num'>Browse</div><div class='step-title'>See tasks</div>"
                "<div class='step-desc'>Explore projects and their tasks in a read-only view.</div></div>"
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info(
                "No employee profile is linked to your account yet. "
                "Ask a manager to link your user account to an employee record on the Employees page."
            )
        st.stop()

    section_title("Workspace at a glance")
    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    total_capacity = sum(e.get("weekly_capacity", 40) for e in employees)
    total_allocated = sum(e.get("current_workload", 0) for e in employees)
    utilization = round((total_allocated / total_capacity) * 100, 1) if total_capacity > 0 else 0
    with c1:
        kpi(len(employees), "Employees", icon="🧑‍💼", accent="blue")
    with c2:
        kpi(len(projects), "Projects", icon="🗂️", accent="violet")
    with c3:
        kpi(len(tasks), "Tasks", icon="✅", accent="indigo")
    with c4:
        kpi(len(assignments), "Assignments", icon="📌", accent="amber")
    with c5:
        kpi(f"{utilization}%", "Allocated", sub=f"{total_allocated:.0f}h / {total_capacity:.0f}h weekly", icon="⚡", accent="green")

    st.markdown("")

    section_title("Quick actions")
    q1, q2, q3, q4, q5 = st.columns(5, gap="small")
    with q1:
        st.page_link("pages/2_Projects.py", label="🗂️ &nbsp; New project", use_container_width=True)
    with q2:
        st.page_link("pages/3_Tasks.py", label="✅ &nbsp; Add task & match", use_container_width=True)
    with q3:
        st.page_link("pages/4_Employees.py", label="🧑‍💼 &nbsp; Manage teams", use_container_width=True)
    with q4:
        st.page_link("pages/6_Assignments.py", label="📌 &nbsp; Approvals & work", use_container_width=True)
    with q5:
        st.page_link("pages/7_AI_Hiring.py", label="🤖 &nbsp; AI Hiring", use_container_width=True)