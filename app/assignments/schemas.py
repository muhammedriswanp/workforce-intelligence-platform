from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AssignmentCreate(BaseModel):
    task_id: int
    employee_id: int
    allocated_hours: float


class AssignmentResponse(BaseModel):
    id: int
    task_id: int
    employee_id: int
    allocated_hours: float
    status: str
    assigned_at: datetime

    class Config:
        from_attributes = True


class AssignmentRejectionRequest(BaseModel):
    task_id: int
    employee_id: int
    reason: str


class AssignmentActionResponse(BaseModel):
    message: str
    assignment_id: Optional[int] = None
    task_id: int
    employee_id: int
    status: str
