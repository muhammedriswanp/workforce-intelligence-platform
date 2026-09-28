from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TaskCreate(BaseModel):
    project_id: int
    title: str
    description: Optional[str] = None
    estimated_hours: float
    status: Optional[str] = "todo"


class TaskResponse(BaseModel):
    id: int
    project_id: int
    title: str
    description: Optional[str]
    estimated_hours: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class TaskDependencyCreate(BaseModel):
    prerequisite_task_id: int


class TaskDependencyResponse(BaseModel):
    id: int
    task_id: int
    prerequisite_task_id: int

    class Config:
        from_attributes = True


class CandidateMetricBreakdown(BaseModel):
    skill_score: float
    availability_score: float
    workload_score: float
    experience_score: float


class CandidateMatchResponse(BaseModel):
    employee_id: int
    name: Optional[str] = None
    designation: str
    experience_years: int
    final_score: float
    metrics: CandidateMetricBreakdown


class CandidateCapacityCheck(BaseModel):
    employee_id: int
    task_id: int
    task_estimated_hours: float
    current_workload: float
    weekly_capacity: float
    projected_workload: float
    projected_allocation_percentage: float
    can_take_task: bool
