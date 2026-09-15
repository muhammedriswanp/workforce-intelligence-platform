from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session 
from app.database import SessionLocal
from app.schemas import TaskResponse, TaskCreate
from app.auth.dependencies import get_current_user, get_current_manager
from app.models import Project, Task
from sqlalchemy import select

router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),  # Only managers can create tasks
):
    # Verify parent project exists
    project = db.get(Project, task_data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {task_data.project_id} not found",
        )
    new_task = Task(
        project_id=task_data.project_id,
        title=task_data.title,
        description=task_data.description,
        estimated_hours=task_data.estimated_hours,
        status=task_data.status or "todo",
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/project/{project_id}", response_model=list[TaskResponse])
def list_tasks_for_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    statement = select(Task).where(Task.project_id == project_id).order_by(Task.id)
    return db.execute(statement).scalars().all()

@router.get("/{id}", response_model=TaskResponse)
def get_task(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    task = db.get(Task, id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {id} not found",
        )
    return task