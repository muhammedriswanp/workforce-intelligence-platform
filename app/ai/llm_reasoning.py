from langchain_core.messages import HumanMessage, SystemMessage
from app.ai.task_analyzer import llm

SYSTEM_REASONING_PROMPT = """You are an AI Workforce Intelligence Assistant.
Your job is to provide clear, grounded, and professional explanations for candidate recommendations.

Follow these strict constraints:
1. Explain WHY the candidate is recommended based on matched skills, workload capacity, and organizational policies.
2. If any required skills are missing, acknowledge the gap briefly.
3. Keep your explanation strictly between 1 to 2 sentences.
4. Do not invent facts, work history, or policy rules not provided in the prompt.
"""

def generate_recommendation_explanation(
    candidate_name: str,
    designation: str,
    matched_skills: list[str],
    missing_skills: list[str],
    available_hours: float,
    weekly_capacity: float,
    match_score: float,
    task_role: str,
    task_skills: list[str],
    task_complexity: str,
    policy_context: str,
) -> str:
    """Uses LLM reasoning to generate an explainable justification

    grounded in structured workforce metrics and retrieved RAG policies.
    """
    user_prompt = f"""Task Context:
- Target Role: {task_role}
- Required Skills: {', '.join(task_skills)}
- Complexity: {task_complexity}

Candidate Profile:
- Name: {candidate_name} ({designation})
- Matched Skills: {', '.join(matched_skills) if matched_skills else 'None'}
- Missing Skills: {', '.join(missing_skills) if missing_skills else 'None'}
- Available Capacity: {available_hours} hrs / {weekly_capacity} hrs
- Calculated Match Score: {match_score}%

Organizational Policies & Guidelines:
{policy_context}

Generate a concise 1-2 sentence recommendation justification:"""
    messages = [
        SystemMessage(content=SYSTEM_REASONING_PROMPT),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return (
        response.content.strip()
        if hasattr(response, "content")
        else str(response).strip()
    )