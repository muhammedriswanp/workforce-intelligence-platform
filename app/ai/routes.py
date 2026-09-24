from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_manager
from app.schemas import TaskAnalysisRequest, TaskAnalysisResult, TaskRecommendationResponse
from app.ai.task_analyzer import analyze_task_description
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.ai.candidate_evaluator import evaluate_candidates_for_task 

router = APIRouter(prefix="/ai", tags=["AI & Workforce Intelligence"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze-task", response_model=TaskAnalysisResult)
def analyze_task(
    payload: TaskAnalysisRequest,
    current_user: dict = Depends(get_current_manager),
):
    return analyze_task_description(payload.description)
