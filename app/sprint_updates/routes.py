from fastapi import APIRouter, status, Depends, HTTPException, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.auth.dependencies import get_current_user
from app.models import Employee, Assignment, SprintUpdate
from app.sprint_updates.schemas import SprintUpdateCreate, SprintUpdateResponse
from app.sprint_updates.vector_service import index_sprint_update

router = APIRouter(prefix="/sprint-updates", tags=["Sprint Updates"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=SprintUpdateResponse, status_code=status.HTTP_201_CREATED)
def create_sprint_update(
    data: SprintUpdateCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1. Find the employee from the JWT (never from the request body)
    employee = db.execute(
        select(Employee).where(Employee.user_id == current_user["user_id"])
    ).scalar_one_or_none()
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only employees can post sprint updates",
        )

    # 2. Check the task is actively assigned to this employee
    assignment = db.execute(
        select(Assignment).where(
            Assignment.task_id == data.task_id,
            Assignment.employee_id == employee.id,
            Assignment.status == "active",
        )
    ).scalar_one_or_none()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This task is not assigned to you",
        )

    # 3. Save to PostgreSQL
    update = SprintUpdate(
        employee_id=employee.id,
        task_id=data.task_id,
        update_text=data.update_text.strip(),
    )
    db.add(update)
    db.commit()
    db.refresh(update)

    background_tasks.add_task(
        index_sprint_update,
        update.id,
        employee.id,
        update.task_id,
        update.update_text,
        update.created_at,
    )

    return update