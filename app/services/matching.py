from app.models.employee import Employee, EmployeeSkill
from app.models.task import Task

def calculate_employee_score(
    employee: Employee,
    task: Task,
    employee_skills: list[EmployeeSkill],
    total_allocated_hours: float,
) -> dict:
    # 1. Availability Score (25%)
    capacity = employee.weekly_capacity if employee.weekly_capacity > 0 else 40.0
    free_hours = max(0.0, capacity - total_allocated_hours)
    # Available if they have at least enough free hours to cover the task
    availability_score = min(100.0, (free_hours / task.estimated_hours) * 100.0) if task.estimated_hours > 0 else 100.0

    # 2. Workload Score (20%) - Lower workload gets a higher score
    current_allocation_pct = (total_allocated_hours / capacity) * 100.0
    workload_score = max(0.0, 100.0 - current_allocation_pct)

    # 3. Experience Score (15%) - Cap at 10 years for a full 100% score
    experience_score = min(100.0, (employee.experience_years / 10.0) * 100.0)

    # 4. Skill Match Score (40%) - Base score for holding relevant skills
    # (Matches proficiency: Beginner=50%, Intermediate=75%, Advanced=100%)
    skill_weights = {"Beginner": 50.0, "Intermediate": 75.0, "Advanced": 100.0}
    skill_score = 0.0
    if employee_skills:
        scores = [skill_weights.get(es.proficiency_level, 50.0) for es in employee_skills]
        skill_score = sum(scores) / len(scores)

    # Final Weighted Aggregate Score
    final_score = (
        (skill_score * 0.40)
        + (availability_score * 0.25)
        + (workload_score * 0.20)
        + (experience_score * 0.15)
    )

    return {
        "employee_id": employee.id,
        "designation": employee.designation,
        "experience_years": employee.experience_years,
        "final_score": round(final_score, 2),
        "metrics": {
            "skill_score": round(skill_score, 2),
            "availability_score": round(availability_score, 2),
            "workload_score": round(workload_score, 2),
            "experience_score": round(experience_score, 2),
        },
    }
    