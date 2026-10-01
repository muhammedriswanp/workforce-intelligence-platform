from fastapi import APIRouter, Depends, HTTPException, status
from app.auth.dependencies import get_current_manager
from app.agent.schemas import TaskRecommendationRequest, TaskRecommendationResponse
from app.ai.schemas import CandidateRecommendation
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
    Runs the employee recommendation workflow for a specific task.

USE THIS TOOL when the manager wants to:
- find suitable employees for a task
- recommend employees for a task
- rank employees based on skills and availability
- get the best candidates for a task
- analyze a task and determine which employees should be assigned

INPUT:
- task_description: The specific task that needs an employee.

WORKFLOW:
1. Analyze the task to identify target role, required skills, and complexity.
2. Find employees.
3. Match employee skills with required skills.
4. Check employee availability.
5. Calculate workload/fit score.
6. Retrieve relevant company policies using RAG.
7. Rank candidates.
8. Generate explanations for the top recommendations.

OUTPUT:
Returns the target role, required skills, complexity, policy context, and ranked employee recommendations.

DO NOT use this tool for:
- creating a task
- listing tasks
- getting an existing task
- assigning an employee directly
- approving/rejecting an assignment
    """
    description =  payload.task_description
    if not description or not description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project or task description cannot be empty",
        )

    # Prepare initial state
    initial_state = {
        "task_description": description,
        "project_id": None,
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
        recommendations=result.get("final_recommendations", []),
    )