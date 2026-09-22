from fastapi import APIRouter, status, Depends, HTTPException
from app.database import SessionLocal
from app.schemas import EmployeeResponse, EmployeeCreate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_manager, get_current_user
from app.models import Employee, User, Assignment
from sqlalchemy import select, func
from app.schemas import EmployeeSkillResponse, EmployeeSkillAssign, WorkloadResponse, AvailabilityResponse
from app.models import Skill, EmployeeSkill

router = APIRouter(prefix="/employees", tags=["Employees"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee_data: EmployeeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_manager),
):
    user = db.get(User, employee_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {employee_data.user_id} does not exist",
        )
    existing_profile = db.execute(
        select(Employee).where(Employee.user_id == employee_data.user_id)
    ).scalar_one_or_none()
    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee profile already exists for this user",
        )
    new_employee = Employee(
        user_id = employee_data.user_id,
        designation=employee_data.designation,
        experience_years=employee_data.experience_years,
        weekly_capacity=employee_data.weekly_capacity,
        current_workload=0.0,
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

@router.get("/", response_model=list[EmployeeResponse])
def list_employees(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    statement = select(Employee).order_by(Employee.id)
    employees = db.execute(statement).scalars().all()
    user_ids = [e.user_id for e in employees]
    names = {}
    if user_ids:
        users = db.execute(select(User).where(User.id.in_(user_ids))).scalars().all()
        names = {u.id: u.name for u in users}
    for e in employees:
        e.name = names.get(e.user_id)
    return employees

@router.get("/{id}", response_model=EmployeeResponse)
def get_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found",
        )
    user = db.get(User, employee.user_id)
    employee.name = user.name if user else None
    return employee

@router.post("/{id}/skills", response_model=EmployeeSkillResponse, status_code=status.HTTP_201_CREATED)
def assign_skill_to_employee(
    id: int,
    skill_data: EmployeeSkillAssign,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_manager),  
):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {id} not found",
        )

    # 2. Check if skill exists
    skill = db.get(Skill, skill_data.skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill with id {skill_data.skill_id} not found",
        )

    # 3. Prevent assigning the same skill twice
    existing_link = db.execute(
        select(EmployeeSkill).where(
            EmployeeSkill.employee_id == id,
            EmployeeSkill.skill_id == skill_data.skill_id,            
        )
    ).scalar_one_or_none()
    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already assigned to this employee",
        )

    # 4. Create bridge record
    new_assignment = EmployeeSkill(
        employee_id=id,
        skill_id=skill_data.skill_id,
        proficiency_level=skill_data.proficiency_level,
    )
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    return {
        "skill_id": skill.id,
        "skill_name": skill.name,
        "proficiency_level": new_assignment.proficiency_level,
    }

@router.get("/{id}/skills", response_model=list[EmployeeSkillResponse])
def get_employee_skills(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {id} not found",
        )

    # Query employee skills with their names
    statement = (
        select(EmployeeSkill, Skill.name)
        .join(Skill, EmployeeSkill.skill_id == Skill.id)
        .where(EmployeeSkill.employee_id == id)
    )
    results = db.execute(statement).all()

    return [
        {
            "skill_id": item.EmployeeSkill.skill_id,
            "skill_name": item.name,
            "proficiency_level": item.EmployeeSkill.proficiency_level,
        }
        for item in results
    ]

@router.get("/{id}/workload", response_model=WorkloadResponse)
def get_employee_workload(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with id {id} not found")

    # Sum all active assignment hours directly from database
    total_hours = db.execute(
        select(func.coalesce(func.sum(Assignment.allocated_hours), 0.0)).where(
            Assignment.employee_id == id,
            Assignment.status == "active"
        )
    ).scalar_one()

    # Prevent division by zero
    capacity = employee.weekly_capacity if employee.weekly_capacity > 0 else 40.0
    workload_pct = round((total_hours / capacity) * 100, 2)

    # Determine status
    if workload_pct > 100:
        status_label = "overloaded"
    elif workload_pct >= 70:
        status_label = "optimal"
    else:
        status_label = "underloaded"

    return {
        "employee_id": employee.id,
        "weekly_capacity": capacity,
        "total_allocated_hours": total_hours,
        "workload_percentage": workload_pct,
        "status": status_label,
    }

@router.get("/{id}/availability", response_model=AvailabilityResponse)
def get_employee_availability(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = db.get(Employee, id)
    if not employee:
        raise HTTPException(status_code=404, detail=f"Employee with id {id} not found")

    total_hours = db.execute(
        select(func.coalesce(func.sum(Assignment.allocated_hours), 0.0)).where(
            Assignment.employee_id == id,
            Assignment.status == "active"
        )
    ).scalar_one()

    capacity = employee.weekly_capacity if employee.weekly_capacity > 0 else 40.0
    available_hrs = max(0.0, capacity - total_hours)
    remaining_pct = max(0.0, round((available_hrs / capacity) * 100, 2))

    return {
        "employee_id": employee.id,
        "weekly_capacity": capacity,
        "available_hours": available_hrs,
        "remaining_capacity_percentage": remaining_pct,
        "is_available": available_hrs > 0,
    }