from sqlalchemy.orm import Session
from app.schemas import TaskAnalysisResult, CandidateRecommendation
from sqlalchemy import select
from app.models import Employee, User, Skill, EmployeeSkill
from app.ai.task_analyzer import llm
from app.rag.retriever import retrieve_relevant_policies
from app.ai.llm_reasoning import generate_recommendation_explanation


def evaluate_candidates_for_task(
    db: Session,
    analysis: TaskAnalysisResult,
)-> list[CandidateRecommendation]:

    query = f"{analysis.role} {' '.join(analysis.skills)} {analysis.complexity}"
    policies = retrieve_relevant_policies(query, k=3)
    policy_context = "\n".join([f"- {p}" for p in policies]) if policies else "Standard assignment rules apply."
    
    # 1. Fetch all employees with their user account and skills
    employees = db.execute(select(Employee)).scalars().all()
    if not employees:
        return []

    candidates = []

    for emp in employees:
        user = db.get(User, emp.user_id)
        user_name = user.name if user else f"Employee {emp.id}"

        # Fetch employee's assigned skills
        emp_skills_query = (
            select(Skill.name, EmployeeSkill.proficiency_level)
            .join(EmployeeSkill, EmployeeSkill.skill_id == Skill.id)
            .where(EmployeeSkill.employee_id == emp.id)
        )
        emp_skills_data = db.execute(emp_skills_query).all()

        emp_skill_map = {row.name.strip().lower(): row.proficiency_level for row in emp_skills_data}

        # 2. Skill Matcher: Calculate overlap
        matched = [name for name in analysis.skills if name.strip().lower() in emp_skill_map]
        missing = [name for name in analysis.skills if name.strip().lower() not in emp_skill_map]

        skill_score = len(matched) / len(analysis.skills) if analysis.skills else 0.0

        # 3. Workload & Availability Checker
        available_hours = max(0.0, emp.weekly_capacity - emp.current_workload)
        availability_ratio = available_hours / emp.weekly_capacity if emp.weekly_capacity > 0 else 0.0

        # Deterministic formula: 60% Skill Match + 40% Available Capacity
        total_score = round((skill_score * 0.60 + availability_ratio * 0.40) * 100, 2)

        candidates.append({
            "employee_id": emp.id,
            "name": user_name,
            "designation": emp.designation,
            "match_score": total_score,
            "matched_skills": matched,
            "missing_skills": missing,
            "weekly_capacity": emp.weekly_capacity,
            "current_workload": emp.current_workload,
            "available_hours": available_hours,
            "years_exp": emp.experience_years
        })

    # Rank candidates by match score descending
    candidates.sort(key=lambda x: x["match_score"], reverse=True)

    # 4. Generate LLM explanations for top matches
    evaluated_recommendations = []
    for cand in candidates[:3]:
        reason = generate_recommendation_explanation(
            candidate_name=cand["name"],
            designation=cand["designation"],
            matched_skills=cand["matched_skills"],
            missing_skills=cand["missing_skills"],
            available_hours=cand["available_hours"],
            weekly_capacity=cand["weekly_capacity"],
            match_score=cand["match_score"],
            task_role=analysis.role,
            task_skills=analysis.skills,
            task_complexity=analysis.complexity,
            policy_context=policy_context,
        )

        evaluated_recommendations.append(
            CandidateRecommendation(
                employee_id=cand["employee_id"],
                name=cand["name"],
                designation=cand["designation"],
                match_score=cand["match_score"],
                matched_skills=cand["matched_skills"],
                missing_skills=cand["missing_skills"],
                weekly_capacity=cand["weekly_capacity"],
                current_workload=cand["current_workload"],
                available_hours=cand["available_hours"],
                reason=reason,
            )
        )

    return evaluated_recommendations