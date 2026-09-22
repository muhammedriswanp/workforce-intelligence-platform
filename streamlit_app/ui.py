import streamlit as st

FONT = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"

PILL_PALETTE = {
    "planning": ("#93c5fd", "#1e3a8a"),
    "in_progress": ("#fcd34d", "#78350f"),
    "completed": ("#6ee7b7", "#064e3b"),
    "todo": ("#cbd5e1", "#334155"),
    "active": ("#93c5fd", "#1e3a8a"),
    "cancelled": ("#fca5a5", "#7f1d1d"),
    "underloaded": ("#6ee7b7", "#064e3b"),
    "optimal": ("#fcd34d", "#78350f"),
    "overloaded": ("#fca5a5", "#7f1d1d"),
    "manager": ("#c4b5fd", "#4c1d95"),
    "employee": ("#93c5fd", "#1e3a8a"),
    "beginner": ("#cbd5e1", "#334155"),
    "intermediate": ("#93c5fd", "#1e3a8a"),
    "advanced": ("#c4b5fd", "#4c1d95"),
}

ACCENTS = {
    "blue": "#60a5fa",
    "violet": "#818cf8",
    "indigo": "#a5b4fc",
    "amber": "#fbbf24",
    "green": "#34d399",
    "rose": "#fb7185",
}


def apply_theme():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] { font-family: __FONT__; }

        .stApp {
            background: radial-gradient(1100px 480px at 100% 0%, rgba(79,70,229,0.18) 0%, rgba(79,70,229,0) 60%),
                        radial-gradient(1100px 480px at 0% 0%, rgba(37,99,235,0.16) 0%, rgba(37,99,235,0) 60%),
                        linear-gradient(180deg, #0b1220 0%, #0f172a 100%);
        }

        [data-testid="stHeader"] { background: rgba(11,18,32,0.75); backdrop-filter: blur(6px); }

        [data-testid="stSidebarNav"] { display: none; }

        .side-nav { display: flex; flex-direction: column; gap: 4px; margin-top: 4px; }
        .side-nav .side-head { font-size: 0.7rem; font-weight: 800; letter-spacing: 0.06em; color: #64748b; text-transform: uppercase; margin: 12px 0 2px 10px; }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 60%, #0f172a 100%);
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] * { color: #cbd5e1; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] ul li a { color: #94a3b8; font-weight: 500; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] ul li a:hover { background: rgba(255,255,255,0.06); color: #e2e8f0; }
        [data-testid="stSidebar"] [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
            background: rgba(255,255,255,0.08);
            border-left: 3px solid #818cf8;
            color: #ffffff;
        }

        h1, h2, h3 { color: #f1f5f9; letter-spacing: -0.02em; }

        p, label, .stMarkdown p, .stCaption, [data-testid="stCaptionContainer"] { color: #cbd5e1; }
        .stMarkdown { color: #cbd5e1; }

        .stButton > button {
            border-radius: 10px; border: 1px solid #334155; background: #312e81; color: #e0e7ff; font-weight: 600;
            transition: transform 0.12s ease, box-shadow 0.12s ease;
        }
        .stButton > button:hover { background: #4338ca; border-color: #6366f1; color: #ffffff; transform: translateY(-1px); }
        .stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #4f46e5, #6366f1); border: none; color: #ffffff;
            box-shadow: 0 6px 16px rgba(79,70,229,0.35);
        }
        .stButton > button[kind="primary"]:hover { background: linear-gradient(135deg, #6366f1, #818cf8); }
        .stButton > button[kind="secondary"] { background: #1e293b; color: #a5b4fc; }
        .stButton > button[kind="secondary"]:hover { background: #24324a; color: #c7d2fe; }

        .stTextInput input, .stTextArea textarea, .stNumberInput input, .stSelectbox > div > div {
            border-radius: 10px; border: 1px solid #334155; background: #0f172a; color: #e2e8f0;
        }
        .stTextInput input:focus, .stTextArea textarea:focus, .stNumberInput input:focus { border-color: #6366f1; }
        .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #64748b; }

        div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; border: 1px solid #1e293b; }

        [data-baseweb="select"] [data-testid="stSelectbox"] div div { color: #e2e8f0; }
        div[data-baseweb="popover"] ul li { background: #111a2e; color: #e2e8f0; }

        .hero {
            padding: 1.4rem 1.7rem; border-radius: 20px;
            background: linear-gradient(120deg, #1e1b4b 0%, #4338ca 55%, #6366f1 130%);
            color: #ffffff; box-shadow: 0 14px 30px rgba(49,46,129,0.45); margin-bottom: 1.4rem;
            border: 1px solid rgba(165,180,252,0.25);
        }
        .hero h1 { color: #ffffff; margin: 0; font-weight: 800; }
        .hero p { color: #e0e7ff; margin: 0.25rem 0 0 0; }

        .ph { display: flex; align-items: center; gap: 0.9rem; margin-bottom: 1.1rem; }
        .ph-icon {
            font-size: 1.5rem; width: 52px; height: 52px; display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, rgba(99,102,241,0.25), rgba(129,140,248,0.12));
            border: 1px solid rgba(129,140,248,0.3); border-radius: 14px;
        }
        .ph h2 { margin: 0; }
        .ph p { margin: 0; }

        .kpi {
            background: #111a2e; border: 1px solid #24324a; border-radius: 16px; padding: 14px 18px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.35); display: flex; align-items: center; gap: 14px; height: 100%;
        }
        .kpi-icon {
            width: 46px; height: 46px; border-radius: 14px; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center; font-size: 1.4rem;
            background: var(--accent-soft, rgba(99,102,241,0.18)); color: var(--accent, #818cf8);
        }
        .kpi-value { font-size: 1.55rem; font-weight: 800; color: #f8fafc; line-height: 1.05; }
        .kpi-label { font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.03em; }
        .kpi-sub { font-size: 0.75rem; color: #64748b; }

        .card {
            background: #111a2e; border: 1px solid #24324a; border-radius: 16px; padding: 1.1rem 1.3rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.35);
        }
        .card-title { font-weight: 700; color: #f1f5f9; font-size: 0.95rem; margin-bottom: 0.35rem; }
        .card-sub { color: #94a3b8; font-size: 0.8rem; }

        .section-title {
            display: flex; align-items: center; gap: 8px; margin: 1.25rem 0 0.5rem;
            font-weight: 800; color: #f1f5f9; font-size: 1.05rem;
        }
        .section-bar { width: 4px; height: 18px; border-radius: 3px; background: linear-gradient(180deg, #6366f1, #a5b4fc); }

        .scorebar { width: 100%; height: 8px; border-radius: 6px; background: #24324a; overflow: hidden; margin: 4px 0; }
        .scorebar-fill { height: 100%; border-radius: 6px; background: linear-gradient(90deg, #6366f1, #818cf8); }

        .tag {
            display: inline-flex; align-items: center; gap: 6px;
            padding: 3px 12px; border-radius: 999px; font-size: 12px; font-weight: 600;
        }

        .alert {
            border-radius: 12px; padding: 10px 14px; display: flex; align-items: center; gap: 10px;
            font-size: 0.9rem; font-weight: 500;
        }

        a[data-testid="stPageLink-NavLink"] { border-radius: 12px; padding: 0.35rem 0; font-weight: 600; color: #a5b4fc; }

        .steps { display: flex; gap: 12px; flex-wrap: wrap; }
        .step {
            flex: 1; min-width: 180px; background: #111a2e; border: 1px solid #24324a; border-radius: 14px;
            padding: 14px; box-shadow: 0 1px 3px rgba(0,0,0,0.35);
        }
        .step-num { font-size: 0.72rem; font-weight: 800; letter-spacing: 0.05em; color: #818cf8; text-transform: uppercase; margin-bottom: 4px; }
        .step-title { font-weight: 700; color: #f1f5f9; font-size: 0.95rem; }
        .step-desc { color: #94a3b8; font-size: 0.8rem; margin-top: 4px; }

        .profile-card {
            background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px; padding: 14px 16px; margin-bottom: 16px;
        }
        .profile-avatar {
            width: 40px; height: 40px; border-radius: 50%;
            background: linear-gradient(135deg, #a5b4fc, #6366f1);
            display: flex; align-items: center; justify-content: center; font-weight: 800; color: #1e1b4b; font-size: 1rem;
        }
        .profile-name { font-weight: 700; color: #ffffff; font-size: 0.95rem; }
        .profile-sub { color: #a5b4fc; font-size: 0.75rem; }

        code { background: rgba(99,102,241,0.18); color: #c7d2fe; border-radius: 6px; padding: 1px 6px; }

        hr { border-color: #24324a; }
        </style>
        """.replace("__FONT__", FONT),
        unsafe_allow_html=True,
    )


def hero(title, subtitle):
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def page_header(emoji, title, subtitle=None):
    subtitle_html = f'<div class="card-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="ph"><div class="ph-icon">{emoji}</div>'
        f'<div><h2 style="margin:0">{title}</h2>{subtitle_html}</div></div>',
        unsafe_allow_html=True,
    )


def section_title(text):
    st.markdown(
        f'<div class="section-title"><span class="section-bar"></span>{text}</div>',
        unsafe_allow_html=True,
    )


def kpi(value, label, sub=None, icon="📊", accent="violet"):
    accent_color = ACCENTS.get(accent, ACCENTS["violet"])
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(
        f'<div class="kpi" style="--accent:{accent_color};'
        f'--accent-soft:{accent_color}2E;">'
        f'<div class="kpi-icon">{icon}</div><div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-label">{label}</div>{sub_html}</div></div>',
        unsafe_allow_html=True,
    )


def status_pill(status):
    fg, bg = PILL_PALETTE.get(str(status).lower(), ("#cbd5e1", "#334155"))
    return (
        f'<span class="tag" style="color:{fg};background:{bg};">{status}</span>'
    )


def tag(text, kind="neutral"):
    fg, bg = PILL_PALETTE.get(str(kind).lower(), ("#cbd5e1", "#334155"))
    return f'<span class="tag" style="color:{fg};background:{bg};">{text}</span>'


def display_name(entity, fallback_prefix="Employee"):
    if not entity:
        return fallback_prefix
    name = entity.get("name")
    if name:
        return name
    designation = entity.get("designation")
    if designation:
        return designation
    entity_id = entity.get("id")
    return f"{fallback_prefix} #{entity_id}" if entity_id is not None else fallback_prefix


def card(title=None, sub=None):
    if title:
        st.markdown(f'<div class="card"><div class="card-title">{title}</div>{sub or ""}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="card">{sub or ""}</div>', unsafe_allow_html=True)


def score_bar(score):
    s = max(0.0, min(100.0, float(score or 0)))
    return (
        f'<div style="display:flex;align-items:center;gap:10px;">'
        f'<div class="scorebar"><div class="scorebar-fill" style="width:{s:.0f}%"></div></div>'
        f'<b style="color:#f8fafc;min-width:44px;text-align:right;">{s:.1f}</b></div>'
    )


def alert_markup(icon, text, kind):
    palette = {
        "danger": ("rgba(127,29,29,0.35)", "#fca5a5", "#b91c1c"),
        "warn": ("rgba(120,53,15,0.35)", "#fcd34d", "#b45309"),
        "ok": ("rgba(6,78,59,0.35)", "#6ee7b7", "#059669"),
        "info": ("rgba(30,58,138,0.35)", "#93c5fd", "#2563eb"),
    }
    bg, fg, bar = palette.get(kind, palette["info"])
    st.markdown(
        f'<div class="alert" style="background:{bg};color:{fg};border-left:4px solid {bar};">'
        f'<span>{icon}</span><span>{text}</span></div>',
        unsafe_allow_html=True,
    )


def sidebar_profile():
    user_id = st.session_state.get("user_id")
    role = st.session_state.get("role")
    name = st.session_state.get("name")
    email = st.session_state.get("email")
    if not st.session_state.get("token"):
        return
    display_name = name or f"User #{user_id if user_id is not None else '?'}"
    initial = str(display_name)[0].upper() if display_name else "U"
    role_display = str(role or "user").title()
    sub_parts = [role_display, email]
    sub_html = " &nbsp;|&nbsp; ".join(str(p) for p in sub_parts if p) or role_display
    st.sidebar.markdown(
        f'<div class="profile-card"><div style="display:flex;align-items:center;gap:12px;">'
        f'<div class="profile-avatar">{initial}</div><div>'
        f'<div class="profile-name">{display_name}</div>'
        f'<div class="profile-sub">{sub_html}</div></div></div></div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("Logout", use_container_width=True, key="sidebar_logout"):
        for key in ("token", "role", "user_id", "name", "email"):
            st.session_state[key] = None
        try:
            st.switch_page("app.py")
        except Exception:
            st.rerun()


def require_auth():
    if not st.session_state.get("token"):
        st.warning("Please log in from the home page first.")
        st.stop()


def require_role(*roles):
    if not st.session_state.get("token"):
        st.warning("Please log in from the home page first.")
        st.stop()
    if st.session_state.get("role") not in roles:
        st.error("You don't have permission to access this area.")
        st.stop()


def build_nav():
    if not st.session_state.get("token"):
        st.sidebar.markdown('<div class="side-head">Workspace</div>', unsafe_allow_html=True)
        if st.sidebar.button("Sign in / Create account", use_container_width=True, key="nav_signin"):
            try:
                st.switch_page("app.py")
            except Exception:
                st.rerun()
        return
    role = st.session_state.get("role")
    st.sidebar.markdown('<div class="side-head">Workspace</div>', unsafe_allow_html=True)
    if role == "manager":
        links = [
            ("1_Dashboard.py", "Dashboard"),
            ("2_Projects.py", "Projects"),
            ("3_Tasks.py", "Tasks"),
            ("4_Employees.py", "Employees"),
            ("5_Skills.py", "Skills"),
            ("6_Assignments.py", "Assignments"),
            ("7_AI_Hiring.py", "AI Hiring"),
        ]
    elif role == "employee":
        links = [
            ("1_My_Workspace.py", "My Workspace"),
            ("2_View_Tasks.py", "View Tasks"),
        ]
    else:
        links = []
    for file_name, label in links:
        st.sidebar.page_link(f"pages/{file_name}", label=label, use_container_width=True)


def render_sidebar():
    sidebar_profile()
    build_nav()


def is_manager():
    return st.session_state.get("role") == "manager"