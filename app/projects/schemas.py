from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "planning"


class ProjectResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class TaskProposal(BaseModel):
    title: str = Field(description="Clear, actionable title of the task")
    description: str = Field(description="Brief explanation of work to be performed")
    estimated_hours: float = Field(description="Estimated hours (e.g. 10.0 to 40.0)")
    required_skills: List[str] = Field(description="Key skills required (e.g. ['Python', 'FastAPI'])")


class ProjectDecompositionResponse(BaseModel):
    project_id: int
    proposed_tasks: List[TaskProposal] = Field(description="Maximum 10 broken down tasks")


class BatchTaskApprovalRequest(BaseModel):
    tasks: List[TaskProposal]
