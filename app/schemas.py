from pydantic import BaseModel, EmailStr, Field
from typing import Literal, Optional, List, Any
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

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

class CandidateCapacityCheck(BaseModel):
    employee_id: int
    task_id: int
    task_estimated_hours: float
    current_workload: float
    weekly_capacity: float
    projected_workload: float
    projected_allocation_percentage: float
    can_take_task: bool

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

class TaskRecommendationRequest(BaseModel):
    task_description: str


class TaskRecommendationResponse(BaseModel):
    target_role: str
    required_skills: list[str]
    complexity: str
    policy_context: str
    recommendations: list[dict[str, Any]]

class AssignmentRejectionRequest(BaseModel):
    task_id: int
    employee_id: int
    reason: str

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

class AssignmentActionResponse(BaseModel):
    message: str
    assignment_id: Optional[int] = None
    task_id: int
    employee_id: int
    status: str

