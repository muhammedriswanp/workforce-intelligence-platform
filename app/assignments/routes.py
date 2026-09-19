from fastapi import APIRouter, status, Depends, HTTPException
from app.database import SessionLocal
from app.schemas import AssignmentResponse, AssignmentCreate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_manager, get_current_user
router = APIRouter(prefix="/assignments", tags=["Assignments"])
from app.models import Task, Employee, Assignment
from sqlalchemy import select
from app.services.assignment_service import create_or_approve_assignment

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED
)
def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    # 1. Validate task exists
    task = db.get(Task, data.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {data.task_id} not found",
        )

    # 2. Validate employee exists
    employee = db.get(Employee, data.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {data.employee_id} not found",
        )

    # 3. Prevent duplicate active assignment for the same task & employee
    existing = db.execute(
        select(Assignment).where(
            Assignment.task_id == data.task_id,
            Assignment.employee_id == data.employee_id,
            Assignment.status == "active",
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee is already actively assigned to this task",
        )

    # 4. Create assignment
    new_assignment = Assignment(
        task_id=data.task_id,
        employee_id=data.employee_id,
        allocated_hours=data.allocated_hours,
        status="active",
    )
    db.add(new_assignment)

    # 5. Update employee's current_workload
    employee.current_workload += data.allocated_hours

    db.commit()
    db.refresh(new_assignment)
    return new_assignment

@router.get("/", response_model=list[AssignmentResponse])
def list_assignments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    statement = select(Assignment).order_by(Assignment.id)
    return db.execute(statement).scalars().all()


@router.get("/employee/{employee_id}", response_model=list[AssignmentResponse])
def get_employee_assignments(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    statement = (
        select(Assignment)
        .where(Assignment.employee_id == employee_id)
        .order_by(Assignment.id)
    )
    return db.execute(statement).scalars().all()

@router.post("/approve", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
def approve_assignment(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    return create_or_approve_assignment(db=db, assignment_data=assignment_data)