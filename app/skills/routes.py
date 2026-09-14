from fastapi import APIRouter, status, Depends, HTTPException
from app.database import SessionLocal
from app.schemas import SkillResponse, SkillCreate
from sqlalchemy.orm import Session
from app.auth.dependencies import get_current_manager, get_current_user
from sqlalchemy import select
from app.models.skill import Skill

router = APIRouter(prefix='/skills', tags=['Skills'])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/",response_model=SkillResponse, status_code = status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_manager)
):
    statement = select(Skill).where(Skill.name.ilike(skill_data.name.strip()))
    existing_skill = db.execute(statement).scalar_one_or_none()
    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Skill '{skill_data.name}' already exists",
        )
    new_skill = Skill(name=skill_data.name.strip())
    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)
    return new_skill

@router.get("/", response_model=list[SkillResponse])
def list_skills(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    statement = select(Skill).order_by(Skill.name)
    skills = db.execute(statement).scalars().all()
    return skills