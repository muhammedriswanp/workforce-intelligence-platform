import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from app.schemas import TaskAnalysisResult

load_dotenv()

# Setup Groq LLM using an active model from your account
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0.0,
    api_key=os.getenv("GROQ_API_KEY"),
)

parser = JsonOutputParser(pydantic_object=TaskAnalysisResult)


def analyze_task_description(description: str) -> TaskAnalysisResult:
    """Analyzes unstructured task text and extracts required role and skills."""
    format_instructions = parser.get_format_instructions()

    prompt = f"""
    You are an expert technical project lead.
    Analyze the following task description and extract:
    1. The primary job role needed.
    2. A list of specific technical skills required.
    3. Complexity rating ("Low", "Medium", or "High").

    Task Description:
    \"\"\"{description}\"\"\"

    {format_instructions}
    Respond ONLY with valid json.
    """

    response = llm.invoke(prompt)

    # If the response is an AIMessage, parse its content into a dictionary
    raw_content = (
        response.content if hasattr(response, "content") else str(response)
    )
    parsed_json = parser.parse(raw_content)

    return TaskAnalysisResult(**parsed_json)