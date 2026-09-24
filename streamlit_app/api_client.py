import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"


def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_get(endpoint):
    return requests.get(f"{API_BASE_URL}{endpoint}", headers=get_headers())


def api_post(endpoint, json_data=None):
    return requests.post(
        f"{API_BASE_URL}{endpoint}", json=json_data, headers=get_headers()
    )


def raw_get(endpoint):
    return requests.get(f"{API_BASE_URL}{endpoint}")


def clear_cache():
    st.cache_data.clear()


def safe_json(response, default=None):
    try:
        if response.status_code in (200, 201):
            return response.json()
    except Exception:
        pass
    return default


def login_user(email, password):
    return requests.post(
        f"{API_BASE_URL}/auth/login",
        data={"username": email, "password": password},
    )


def register_user(name, email, password, role):
    payload = {"name": name, "email": email, "password": password, "role": role}
    return requests.post(f"{API_BASE_URL}/auth/register", json=payload)


def get_current_user():
    return safe_json(api_get("/auth/me"), {}).get("user", {})


@st.cache_data(ttl=15, show_spinner=False)
def get_users():
    return safe_json(api_get("/auth/users"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_employees():
    return safe_json(api_get("/employees/"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_employee(employee_id):
    return safe_json(api_get(f"/employees/{employee_id}"), None)


@st.cache_data(ttl=15, show_spinner=False)
def get_workload(employee_id):
    return safe_json(api_get(f"/employees/{employee_id}/workload"), None)


@st.cache_data(ttl=15, show_spinner=False)
def get_availability(employee_id):
    return safe_json(api_get(f"/employees/{employee_id}/availability"), None)


@st.cache_data(ttl=15, show_spinner=False)
def get_employee_skills(employee_id):
    return safe_json(api_get(f"/employees/{employee_id}/skills"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_skills():
    return safe_json(api_get("/skills/"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_projects():
    return safe_json(api_get("/projects/"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_project(project_id):
    return safe_json(api_get(f"/projects/{project_id}"), None)


@st.cache_data(ttl=15, show_spinner=False)
def get_tasks_for_project(project_id):
    return safe_json(api_get(f"/tasks/project/{project_id}"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_task(task_id):
    return safe_json(api_get(f"/tasks/{task_id}"), None)


@st.cache_data(ttl=15, show_spinner=False)
def get_task_dependencies(task_id):
    return safe_json(api_get(f"/tasks/{task_id}/dependencies"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_task_candidates(task_id):
    return safe_json(api_get(f"/tasks/{task_id}/candidates"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_assignments():
    return safe_json(api_get("/assignments/"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_employee_assignments(employee_id):
    return safe_json(api_get(f"/assignments/employee/{employee_id}"), [])


@st.cache_data(ttl=15, show_spinner=False)
def get_all_tasks():
    tasks = []
    for project in get_projects():
        tasks.extend(get_tasks_for_project(project["id"]))
    return tasks


@st.cache_data(ttl=15, show_spinner=False)
def task_lookup():
    return {t["id"]: t for t in get_all_tasks()}


@st.cache_data(ttl=15, show_spinner=False)
def employee_lookup():
    return {e["id"]: e for e in get_employees()}


def analyze_task(description):
    return api_post("/ai/analyze-task", {"description": description})


def recommend_candidates(description):
    return api_post("/agent/recommendations", {"task_description": description})