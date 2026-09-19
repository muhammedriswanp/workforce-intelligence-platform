import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

def get_headers():
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def login_user(email, password):
    url = f"{API_BASE_URL}/auth/login"
    data = {"username": email, "password": password}
    response = requests.post(url, data=data)
    return response

def api_get(endpoint):
    return requests.get(f"{API_BASE_URL}{endpoint}", headers=get_headers())

def api_post(endpoint, json_data):
    return requests.post(f"{API_BASE_URL}{endpoint}", json=json_data, headers=get_headers())