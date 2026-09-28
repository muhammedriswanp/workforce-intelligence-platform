from pydantic import BaseModel
from typing import Literal, Optional


class EmployeeCreate(BaseModel):
    user_id: int
    designation: str
    experience_years: int = 0
    weekly_capacity: float = 40.0


class EmployeeResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str] = None
    designation: str
    experience_years: int
    weekly_capacity: float
    current_workload: float

    class Config:
        from_attributes = True


class EmployeeSkillAssign(BaseModel):
    skill_id: int
    proficiency_level: Literal["Beginner", "Intermediate", "Advanced"]


class EmployeeSkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    proficiency_level: str

    class Config:
        from_attributes = True


class WorkloadResponse(BaseModel):
    employee_id: int
    weekly_capacity: float
    total_allocated_hours: float
    workload_percentage: float
    status: str  # "underloaded", "optimal", "overloaded"


class AvailabilityResponse(BaseModel):
    employee_id: int
    weekly_capacity: float
    available_hours: float
    remaining_capacity_percentage: float
    is_available: bool
