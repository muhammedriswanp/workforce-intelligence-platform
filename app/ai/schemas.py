from pydantic import BaseModel
from typing import List


class TaskAnalysisResult(BaseModel):
    role: str
    skills: List[str]
    complexity: str


class TaskAnalysisRequest(BaseModel):
    description: str


class CandidateRecommendation(BaseModel):
    employee_id: int
    name: str
    designation: str
    match_score: float
    matched_skills: List[str]
    missing_skills: List[str]
    weekly_capacity: float
    current_workload: float
    available_hours: float
    reason: str
