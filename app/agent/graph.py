from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes import (
    task_analyzer_node,
    candidate_finder_node,
    skill_matcher_node,
    availability_checker_node,
    workload_checker_node,
    rag_retrieval_node,
    candidate_ranking_node,
    recommendation_node,
)

# 1. Initialize the StateGraph with the schema
workflow = StateGraph(AgentState)

# 2. Add the 8 nodes
workflow.add_node("task_analyzer", task_analyzer_node)
workflow.add_node("candidate_finder", candidate_finder_node)
workflow.add_node("skill_matcher", skill_matcher_node)
workflow.add_node("availability_checker", availability_checker_node)
workflow.add_node("workload_checker", workload_checker_node)
workflow.add_node("rag_retrieval", rag_retrieval_node)
workflow.add_node("candidate_ranking", candidate_ranking_node)
workflow.add_node("recommendation", recommendation_node)


# 3. Connect nodes with directed linear edges
workflow.add_edge(START, "task_analyzer")
workflow.add_edge("task_analyzer", "candidate_finder")
workflow.add_edge("candidate_finder", "skill_matcher")
workflow.add_edge("skill_matcher", "availability_checker")
workflow.add_edge("availability_checker", "workload_checker")
workflow.add_edge("workload_checker", "rag_retrieval")
workflow.add_edge("rag_retrieval", "candidate_ranking")
workflow.add_edge("candidate_ranking", "recommendation")
workflow.add_edge("recommendation", END)

# 4. Compile into an executable LangGraph app
agent_graph = workflow.compile()