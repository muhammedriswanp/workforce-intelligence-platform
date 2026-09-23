from app.agent.state import AgentState
from app.ai.task_analyzer import analyze_task_description
from app.database import SessionLocal
from sqlalchemy import select
from app.models import Employee, User, Skill, EmployeeSkill
from app.rag.retriever import retrieve_relevant_policies
from app.ai.llm_reasoning import generate_recommendation_explanation

# Node 1: Task Analyzer
def task_analyzer_node(state: AgentState) -> dict:
    """Extracts target role, required skills, and complexity using SLM/LLM."""
    analysis = analyze_task_description(state["task_description"])
    return {
        "target_role": analysis.role,
        "required_skills": analysis.skills,
        "complexity": analysis.complexity,
    }

# Node 2: Candidate Finder
def candidate_finder_node(state: AgentState) -> dict:
    """Fetches all employee profiles from PostgreSQL."""
    db = SessionLocal()
    try:
        employees = db.execute(select(Employee)).scalars().all()
        pool = []
        for emp in employees:
            user = db.get(User, emp.user_id)
            user_name = user.name if user else f"Employee {emp.id}"
            pool.append({
                "employee_id": emp.id,
                "name": user_name,
                "designation": emp.designation,
                "weekly_capacity": emp.weekly_capacity,
                "current_workload": emp.current_workload,
            })
        return {"candidate_pool": pool}
    finally:
        db.close()

# Node 3: Skill Matcher
def skill_matcher_node(state: AgentState) -> dict:
    """Checks skill overlap for each candidate against required skills."""
    db = SessionLocal()
    try:
        required_skills = state.get("required_skills", [])
        candidates = state.get("candidate_pool", [])
        updated_pool = []

        for cand in candidates:
            emp_skills_query = (
                select(Skill.name, EmployeeSkill.proficiency_level)
                .join(EmployeeSkill, EmployeeSkill.skill_id == Skill.id)
                .where(EmployeeSkill.employee_id == cand["employee_id"])
            )
            emp_skills_data = db.execute(emp_skills_query).all()
            emp_skill_map = {row.name.strip().lower(): row.proficiency_level for row in emp_skills_data}

            matched = [s for s in required_skills if s.strip().lower() in emp_skill_map]
            missing = [s for s in required_skills if s.strip().lower() not in emp_skill_map]
            skill_score = len(matched) / len(required_skills) if required_skills else 0.0

            cand_copy = cand.copy()
            cand_copy["matched_skills"] = matched
            cand_copy["missing_skills"] = missing
            cand_copy["skill_score"] = skill_score
            updated_pool.append(cand_copy)

        return {"candidate_pool": updated_pool}
    finally:
        db.close()

# Node 4: Availability Checker
def availability_checker_node(state: AgentState) -> dict:
    """Calculates available remaining hours deterministically."""
    candidates = state.get("candidate_pool", [])
    updated_pool = []

    for cand in candidates:
        cand_copy = cand.copy()
        available = max(0.0, cand["weekly_capacity"] - cand["current_workload"])
        avail_ratio = available / cand["weekly_capacity"] if cand["weekly_capacity"] > 0 else 0.0
        cand_copy["available_hours"] = available
        cand_copy["availability_ratio"] = avail_ratio
        updated_pool.append(cand_copy)

    return {"candidate_pool": updated_pool}


# Node 5: Workload Checker & Scoring
def workload_checker_node(state: AgentState) -> dict:
    """Computes deterministic composite score (Skill 60% + Capacity 40%)."""
    candidates = state.get("candidate_pool", [])
    scored = []

    for cand in candidates:
        cand_copy = cand.copy()
        total_score = round(
            (cand["skill_score"] * 0.60 + cand["availability_ratio"] * 0.40) * 100, 2
        )
        cand_copy["match_score"] = total_score
        scored.append(cand_copy)

    return {"scored_candidates": scored}

# Node 6: RAG Retrieval
def rag_retrieval_node(state: AgentState) -> dict:
    """Retrieves organizational guidelines and assignment policies."""
    query = f"{state.get('target_role', '')} {' '.join(state.get('required_skills', []))} {state.get('complexity', '')}"
    policies = retrieve_relevant_policies(query, k=3)
    policy_context = "\n".join([f"- {p}" for p in policies]) if policies else "Standard assignment rules apply."
    return {"policy_context": policy_context}


# Node 7: Candidate Ranking
def candidate_ranking_node(state: AgentState) -> dict:
    """Sorts candidates by score descending and takes the top matches."""
    candidates = list(state.get("scored_candidates", []))
    candidates.sort(key=lambda x: x["match_score"], reverse=True)
    return {"scored_candidates": candidates[:3]}

# Node 8: Recommendation (Explanation Generation)
def recommendation_node(state: AgentState) -> dict:
    """Uses LLM reasoning to explain top candidate recommendations."""
    final_recs = []
    top_candidates = state.get("scored_candidates", [])

    for cand in top_candidates:
        reason = generate_recommendation_explanation(
            candidate_name=cand["name"],
            designation=cand["designation"],
            matched_skills=cand["matched_skills"],
            missing_skills=cand["missing_skills"],
            available_hours=cand["available_hours"],
            weekly_capacity=cand["weekly_capacity"],
            match_score=cand["match_score"],
            task_role=state.get("target_role", ""),
            task_skills=state.get("required_skills", []),
            task_complexity=state.get("complexity", ""),
            policy_context=state.get("policy_context", ""),
        )

        final_recs.append({
            "employee_id": cand["employee_id"],
            "name": cand["name"],
            "designation": cand["designation"],
            "match_score": cand["match_score"],
            "matched_skills": cand["matched_skills"],
            "missing_skills": cand["missing_skills"],
            "weekly_capacity": cand["weekly_capacity"],
            "current_workload": cand["current_workload"],
            "available_hours": cand["available_hours"],
            "reason": reason,
        })

    return {"final_recommendations": final_recs}