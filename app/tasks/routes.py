from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session 
from app.database import SessionLocal
from app.schemas import TaskResponse, TaskCreate, TaskDependencyCreate, TaskDependencyResponse
from app.auth.dependencies import get_current_user, get_current_manager
from app.models import Project, Task
from sqlalchemy import select
from app.models.task_dependency import TaskDependency

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

@router.post(
    "/{id}/dependencies",
    response_model=TaskDependencyResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_task_dependency(
    id: int,
    dependency_data: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),
):
    # 1. Prevent self-dependency
    if id == dependency_data.prerequisite_task_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A task cannot depend on itself",
        )

    # 2. Check main task exists
    task = db.get(Task, id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {id} not found",
        )

    # 3. Check prerequisite task exists
    prereq = db.get(Task, dependency_data.prerequisite_task_id)
    if not prereq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Prerequisite task with id {dependency_data.prerequisite_task_id} not found",
        )

    # 4. Check duplicate dependency
    existing = db.execute(
        select(TaskDependency).where(
            TaskDependency.task_id == id,
            TaskDependency.prerequisite_task_id
            == dependency_data.prerequisite_task_id,
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This dependency already exists",
        )

    new_dep = TaskDependency(
        task_id=id,
        prerequisite_task_id=dependency_data.prerequisite_task_id,
    )
    db.add(new_dep)
    db.commit()
    db.refresh(new_dep)
    return new_dep

@router.get(
    "/{id}/dependencies", response_model=list[TaskDependencyResponse]
)
def get_task_dependencies(
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

    statement = select(TaskDependency).where(TaskDependency.task_id == id)
    return db.execute(statement).scalars().all()

