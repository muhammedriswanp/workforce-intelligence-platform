from pydantic import BaseModel, EmailStr
from typing import Literal, Optional
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SkillCreate(BaseModel):
    name: str

class SkillResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class EmployeeCreate(BaseModel):
    user_id: int
    designation: str
    experience_years: int = 0
    weekly_capacity: float = 40.0

class EmployeeResponse(BaseModel):
    id: int
    user_id: int
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