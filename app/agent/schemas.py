from pydantic import BaseModel
from typing import Any


class TaskRecommendationRequest(BaseModel):
    task_description: str | None = None
    # project_title: str | None = None
    # project_description: str | None = None
    # project_status: str = "planning"
    # project_id: int | None = None


class TaskRecommendationResponse(BaseModel):
    target_role: str
    required_skills: list[str]
    complexity: str
    policy_context: str
    recommendations: list[dict[str, Any]]
