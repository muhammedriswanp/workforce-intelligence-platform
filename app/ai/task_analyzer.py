import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from app.ai.schemas import TaskAnalysisResult

load_dotenv()

# Setup Groq LLM using an active model from your account
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0.0,
    max_tokens=256,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=TaskAnalysisResult)


def analyze_task_description(description: str) -> TaskAnalysisResult:
    """Analyzes unstructured task text and extracts required role and skills."""
    format_instructions = parser.get_format_instructions()

    prompt = f"""
    You are a technical recruiter and engineering lead.

    Analyze the task and return:
    1. The most relevant job role.
    2. Required technical skills.
    3. Complexity: Low, Medium, or High.

    Skill rules:
    - Prefer concrete, recognizable technologies found in job
    descriptions, such as Python, SQL, PostgreSQL, FastAPI,
    React, Docker, Kubernetes, Kafka, AWS, and PyTorch.
    - Extract technologies explicitly mentioned or clearly required.
    - Do not invent tools or technologies.
    - Avoid abstract skills and practices such as Request Validation,
    Microservices Architecture, Event-Driven Design, Fault Tolerance,
    High Availability, and Error Handling.
    - Do not replace a concept with an unmentioned technology.
    - Return only the relevant skills, usually 3–8.
    - Use standard technology names.

    Role rules:
    - Use a recognizable job title.
    - Do not add seniority unless explicitly required.

    Complexity:
    - Low: simple, limited-scope task.
    - Medium: several components or integrations.
    - High: substantial system design or complex interactions.

    Task Description:
    \"\"\"{description}\"\"\"

    {format_instructions}

    Return only valid JSON matching the required schema.
    """
    
    response = llm.invoke(prompt)

    # If the response is an AIMessage, parse its content into a dictionary
    raw_content = (
        response.content if hasattr(response, "content") else str(response)
    )
    parsed_json = parser.parse(raw_content)

    return TaskAnalysisResult(**parsed_json)