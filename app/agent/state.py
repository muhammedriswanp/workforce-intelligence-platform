from typing import TypedDict, Any

class AgentState(TypedDict):
    # 1. Inputs
    task_description: str
    # project_id: int | None

    # Task analysis
    target_role: str
    required_skills: list[str]
    complexity: str

    # Candidate pipeline
    candidate_pool: list[dict[str, Any]]
    scored_candidates: list[dict[str, Any]]

    # RAG
    policy_context: str

    # Output
    final_recommendations: list[dict[str, Any]]
    error: str | None
    

