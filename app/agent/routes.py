from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_manager
from app.schemas import TaskRecommendationRequest, TaskRecommendationResponse, CandidateRecommendation
from app.agent.graph import agent_graph

router = APIRouter(prefix="/agent", tags=["Agentic Workflow"])

@router.post(
    "/recommendations",
    response_model=TaskRecommendationResponse,
    status_code=status.HTTP_200_OK,
)
def get_recommendations_workflow(
    payload: TaskRecommendationRequest,
    current_manager=Depends(get_current_manager),
):
    """
    Executes the compiled 8-node LangGraph agent workflow:
    START -> Task Analyzer -> Candidate Finder -> Skill Matcher ->
    Availability Checker -> Workload Checker -> RAG Retrieval ->
    Candidate Ranking -> Recommendation (LLM explanation) -> END
    """
    if not payload.task_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task description cannot be empty",
        )

    # Prepare initial state
    initial_state = {
        "task_description": payload.task_description,
        "target_role": "",
        "required_skills": [],
        "complexity": "",
        "candidate_pool": [],
        "scored_candidates": [],
        "policy_context": "",
        "final_recommendations": [],
        "error": None,
    }

    # Execute LangGraph workflow
    result = agent_graph.invoke(initial_state)

    return TaskRecommendationResponse(
        target_role=result.get("target_role", "Developer"),
        required_skills=result.get("required_skills", []),
        complexity=result.get("complexity", "Medium"),
        policy_context=result.get("policy_context", ""),
        recommendations= result.get("final_recommendations", [])
    )