from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from app.database import SessionLocal
from app.models.task import Task
from app.schemas import ProjectCreate, ProjectResponse, TaskProposal
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_manager, get_current_user
from app.models.project import Project
from app.services.task_decomposer import decompose_project_document


router = APIRouter(prefix="/projects", tags=["Projects"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_manager=Depends(get_current_manager),  # Only managers can create projects
):
    new_project = Project(
        title=project_data.title,
        description=project_data.description,
        status=project_data.status,
        created_by=current_manager["user_id"],
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    statement = select(Project).order_by(Project.id)
    return db.execute(statement).scalars().all()

@router.get("/{id}", response_model=ProjectResponse)
def get_project(
    id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = db.get(Project, id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {id} not found",
        )
    return project

@router.post("/{project_id}/decompose", response_model=list[TaskProposal])
def decompose_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_manager = Depends(get_current_manager)
):
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.description:
        raise HTTPException(status_code=400, detail="Project documentation/description is required")

    # Generate up to 10 tasks via LLM
    proposals = decompose_project_document(
        project_id=project.id,
        title=project.title,
        documentation=project.description
    )
    return proposals

@router.post("/{project_id}/tasks/approve-proposal", status_code=status.HTTP_201_CREATED)
def approve_proposed_task(
    project_id: int,
    proposal: TaskProposal,
    db: Session = Depends(get_db),
    current_manager = Depends(get_current_manager)
):
    """Saves an individual reviewed task proposal into the database."""
    new_task = Task(
        project_id=project_id,
        title=proposal.title,
        description=proposal.description,
        estimated_hours=proposal.estimated_hours,
        status="todo"
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return {"message": "Task approved and created", "task_id": new_task.id}