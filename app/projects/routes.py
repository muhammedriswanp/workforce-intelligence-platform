from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from app.database import SessionLocal
from app.schemas import ProjectCreate, ProjectResponse
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_manager, get_current_user
from app.models.project import Project


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