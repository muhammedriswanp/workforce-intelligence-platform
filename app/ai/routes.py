from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.schemas import TaskAnalysisRequest, TaskAnalysisResult, TaskRecommendationResponse
from app.ai.task_analyzer import analyze_task_description
from app.database import SessionLocal
from sqlalchemy.orm import Session
from app.ai.candidate_evaluator import evaluate_candidates_for_task 

router = APIRouter(prefix="/ai", tags=["AI Task Analysis"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/analyze-task", response_model=TaskAnalysisResult)
def analyze_task(
    payload: TaskAnalysisRequest,
    current_user: dict = Depends(get_current_user),
):
    return analyze_task_description(payload.description)

@router.post("/recommend-candidates", response_model=TaskRecommendationResponse)
def recommend_candidates(
    payload: TaskAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Task Analyzer -> Database Lookup -> Skill Matcher -> Availability Checker -> Ranked Candidates
    """
    # 1. AI Task Analysis
    analysis = analyze_task_description(payload.description)

    # 2. Database evaluation & scoring
    ranked_candidates = evaluate_candidates_for_task(db=db, analysis=analysis)

    return TaskRecommendationResponse(
        task_role=analysis.role,
        required_skills=analysis.skills,
        complexity=analysis.complexity,
        recommendations=ranked_candidates
    )