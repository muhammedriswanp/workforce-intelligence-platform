from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.schemas import AssignmentCreate
from app.models import Assignment, Task, Employee
from sqlalchemy import select


def create_or_approve_assignment(db: Session, assignment_data: AssignmentCreate) -> Assignment:
    # 1. Verify Task exists
    task = db.get(Task, assignment_data.task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {assignment_data.task_id} not found",
        )

    #2. Verify Employee exists
    employee = db.get(Employee, assignment_data.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {assignment_data.employee_id} not found",
        )

    # 3. Prevent duplicate active assignment for the same task and employee
    existing = db.execute(
        select(Assignment).where(
            Assignment.task_id == assignment_data.task_id,
            Assignment.employee_id == assignment_data.employee_id,
            Assignment.status == "active",
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee is already assigned to this task",
        )

    # 4. Create assignment record
    new_assignment = Assignment(
        task_id=assignment_data.task_id,
        employee_id=assignment_data.employee_id,
        allocated_hours=assignment_data.allocated_hours,
        status="active",
    )
    db.add(new_assignment)

    # 5. Advance Task status to in_progress
    task.status = "in_progress"

    # 6. Update cached employee workload
    employee.current_workload += assignment_data.allocated_hours

    db.commit()
    db.refresh(new_assignment)
    return new_assignment