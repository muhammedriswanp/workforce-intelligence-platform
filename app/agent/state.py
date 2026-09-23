from typing import TypedDict, Any

class AgentState(TypedDict):
    # 1. Inputs
    task_description: str

    # 2. Extracted Requirements (Task Analyzer)
    target_role: str
    required_skills: list[str]
    complexity: str

    # 3. Deterministic Pipeline Data (Candidate Finder, Skill, Availability, Workload)
    candidate_pool: list[dict[str, Any]]
    scored_candidates: list[dict[str, Any]]

    # 4. RAG Knowledge Context
    policy_context: str

    # 5. Final Output & Reasoning
    final_recommendations: list[dict[str, Any]]
    error: str | None
    

