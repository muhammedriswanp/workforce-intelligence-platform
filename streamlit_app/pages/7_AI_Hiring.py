import streamlit as st
from api_client import analyze_task, recommend_candidates
from ui import apply_theme, page_header, kpi, section_title, tag
from ui import require_role, render_sidebar, score_bar, status_pill

st.set_page_config(page_title="AI Hiring Assistant", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")


def ai_unavailable():
    st.error(
        "The AI provider is currently unavailable (Groq returned an access error). "
        "This is usually caused by a revoked or restricted GROQ_API_KEY, or the network blocking the Groq endpoint. "
        "Until it's fixed, use **Tasks → Run candidate matching** for deterministic, database-powered candidate ranking."
    )

page_header("🤖", "AI Hiring Assistant", "Analyze task descriptions and get ranked candidate recommendations")

st.markdown("")
tab_analyze, tab_recommend = st.tabs(["🧠 Analyze Task", "🎯 Recommend Candidates"])

with tab_analyze:
    st.markdown('<div class="card"><div class="card-title">Analyze Task</div>'
                '<div class="card-sub">Describe the work and the AI will infer the role, required skills and complexity.</div></div>',
                unsafe_allow_html=True)
    with st.form("ai_analyze"):
        description = st.text_area(
            "Task description",
            placeholder="e.g. create front end",
            height=120,
        )
        submitted = st.form_submit_button("Analyze Task", use_container_width=True)

    if submitted:
        if not description.strip():
            st.error("Task description is required.")
        else:
            with st.spinner("Analyzing task…"):
                res = analyze_task(description.strip())
                if res.status_code == 200:
                    data = res.json()
                    c1, c2, c3 = st.columns(3, gap="small")
                    with c1:
                        kpi(data.get("role", "—"), "Required role", icon="🧑‍💻", accent="blue")
                    with c2:
                        kpi(data.get("complexity", "—"), "Complexity", icon="🌀", accent="amber")
                    with c3:
                        kpi(len(data.get("skills", [])), "Skills", sub="suggested by AI", icon="⚡", accent="violet")
                    st.markdown("")
                    if data.get("skills"):
                        section_title("Suggested skills")
                        st.markdown(" ".join(tag(s, "intermediate") for s in data["skills"]), unsafe_allow_html=True)
                else:
                    st.error(f"Analysis failed: {res.text}")
                    ai_unavailable()

with tab_recommend:
    st.markdown('<div class="card"><div class="card-title">Recommend Candidates</div>'
                '<div class="card-sub">Task Analyzer → Database Lookup → Skill Matcher → Availability Checker → Ranked Candidates</div></div>',
                unsafe_allow_html=True)
    with st.form("ai_recommend"):
        rec_description = st.text_area(
            "Task description",
            placeholder="e.g. Build a REST API for the customer analytics platform using FastAPI and PostgreSQL.",
            height=120,
        )
        rec_submitted = st.form_submit_button("Recommend Candidates", use_container_width=True)

    if rec_submitted:
        if not rec_description.strip():
            st.error("Task description is required.")
        else:
            with st.spinner("Evaluating candidates…"):
                res = recommend_candidates(rec_description.strip())
                if res.status_code == 200:
                    data = res.json()
                    c1, c2, c3 = st.columns(3, gap="small")
                    with c1:
                        kpi(data.get("target_role", "—"), "Required role", icon="🧑‍💻", accent="blue")
                    with c2:
                        kpi(data.get("complexity", "—"), "Complexity", icon="🌀", accent="amber")
                    with c3:
                        kpi(len(data.get("recommendations", [])), "Candidates", sub="ranked by AI", icon="🎯", accent="violet")

                    st.markdown("")
                    if data.get("required_skills"):
                        section_title("Required skills")
                        st.markdown(" ".join(tag(s, "advanced") for s in data["required_skills"]), unsafe_allow_html=True)

                    recs = data.get("recommendations", [])
                    if recs:
                        st.markdown("")
                        section_title("Ranked candidates")
                        for cand in recs:
                            c_color = "green" if cand.get("match_score", 0) >= 60 else ("amber" if cand.get("match_score", 0) >= 40 else "rose")
                            st.markdown(
                                f'<div class="card">'
                                f'<div class="card-title">{cand.get("name", "—")} '
                                f'<span style="color:#94a3b8;font-weight:600;">· {cand.get("designation", "")}</span></div>'
                                f'{score_bar(cand.get("match_score", 0))}'
                                f'<div class="card-sub" style="margin-top:8px;">'
                                f'<span style="color:#6ee7b7;font-weight:600;">✅ Matched: </span>'
                                f'{(", ".join(cand.get("matched_skills", [])) or "None")} &nbsp;·&nbsp; '
                                f'<span style="color:#fca5a5;font-weight:600;">❌ Missing: </span>'
                                f'{(", ".join(cand.get("missing_skills", [])) or "None")}</div>'
                                f'<div class="card-sub" style="margin-top:6px;">'
                                f'Capacity {cand.get("weekly_capacity", 0):.0f}h · Workload {cand.get("current_workload", 0):.0f}h · '
                                f'Available {cand.get("available_hours", 0):.0f}h</div>'
                                f'<div class="card-sub" style="margin-top:8px;color:#cbd5e1;">💬 {cand.get("reason", "")}</div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.caption("No recommendations returned.")
                else:
                    st.error(f"Recommendation failed: {res.text}")
                    ai_unavailable()