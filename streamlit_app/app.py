import streamlit as st
from api_client import login_user

st.set_page_config(page_title="Workforce Intelligence", layout="wide")

if "token" not in st.session_state:
    st.session_state.token = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

st.title("Workforce Intelligence Platform")

if not st.session_state.token:
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign In")

        if submit:
            res = login_user(email, password)
            if res.status_code == 200:
                data = res.json()
                st.session_state.token = data["access_token"]
                st.success("Logged in successfully! Use the sidebar to navigate.")
                st.rerun()
            else:
                st.error("Invalid email or password.")
else:
    st.success("Authenticated as Active Session")
    if st.button("Logout"):
        st.session_state.token = None
        st.session_state.user_role = None
        st.rerun()