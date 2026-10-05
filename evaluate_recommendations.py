
from langsmith import Client, evaluate

from app.agent.graph import agent_graph


DATASET_NAME = "workforce-recommendation-evaluation"


def run_recommendation(inputs: dict) -> dict:
    """Run the existing LangGraph recommendation workflow."""

    task_description = inputs["task_description"]

    initial_state = {
        "task_description": task_description,
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

    result = agent_graph.invoke(initial_state)

    # Return the fields the evaluator needs to compare.
    return {
        "target_role": result.get("target_role", ""),
        "required_skills": result.get("required_skills", []),
        "complexity": result.get("complexity", ""),
        "recommendations": result.get("final_recommendations", []),
    }


def recommendation_quality(run, example) -> dict:
    """Compare the workflow output with the dataset reference."""

    actual = run.outputs or {}
    expected = example.outputs or {}

    expected_role = expected.get("expected_role", "").strip().lower()
    actual_role = actual.get("target_role", "").strip().lower()

    role_match = (
        1.0
        if expected_role and expected_role in actual_role
        else 0.0
    )

    expected_skills = {
        skill.strip().lower()
        for skill in expected.get("expected_skills", [])
    }
    actual_skills = {
        skill.strip().lower()
        for skill in actual.get("required_skills", [])
    }

    skill_match = (
        len(expected_skills & actual_skills) / len(expected_skills)
        if expected_skills
        else 0.0
    )

    expected_complexity = (
        expected.get("expected_complexity", "").strip().lower()
    )
    actual_complexity = actual.get("complexity", "").strip().lower()

    complexity_match = (
        1.0
        if expected_complexity and expected_complexity == actual_complexity
        else 0.0
    )

    score = (
        role_match * 0.4
        + skill_match * 0.4
        + complexity_match * 0.2
    )

    return {
        "key": "recommendation_quality",
        "score": score,
        "comment": (
            f"Role match: {role_match:.0%}; "
            f"Skill coverage: {skill_match:.0%}; "
            f"Complexity match: {complexity_match:.0%}"
        ),
    }


if __name__ == "__main__":
    client = Client()

    experiment_results = evaluate(
        run_recommendation,
        data=DATASET_NAME,
        evaluators=[recommendation_quality],
        experiment_prefix="workforce-recommendation-evaluation",
    )

    print("Evaluation finished.")
    print(experiment_results)
