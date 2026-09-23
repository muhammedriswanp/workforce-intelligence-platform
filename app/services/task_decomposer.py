from langchain_core.prompts import ChatPromptTemplate
from typing import List
from app.schemas import TaskProposal, ProjectDecompositionResponse
from app.ai.task_analyzer import llm


# Setup prompt instructing the model to produce <= 10 tasks
decomposition_prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert technical project architect. "
     "Analyze the given project title and project documentation. "
     "Decompose the project into no more than 10 concrete, atomic, non-overlapping tasks. "
     "Each task must have an estimated duration (hours) and the required skills."),
    ("human", 
     "Project Title: {title}\n\nProject Documentation:\n{documentation}")
])

def decompose_project_document(project_id: int, title: str, documentation: str) -> List[TaskProposal]:
    # Bind structured output to the shared, pre-configured LLM instance
    structured_llm = llm.with_structured_output(ProjectDecompositionResponse)
    
    chain = decomposition_prompt | structured_llm
    result = chain.invoke({"title": title, "documentation": documentation})
    
    # Strictly enforce the <= 10 tasks limit
    return result.proposed_tasks[:10]