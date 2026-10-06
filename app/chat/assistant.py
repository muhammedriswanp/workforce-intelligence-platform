import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from fastmcp import FastMCP
from fastmcp.client import Client
from main import app
from app.jwt_utils import create_access_token
from langchain_core.chat_history import InMemoryChatMessageHistory

from app.chat.safety_guard import check_safety


load_dotenv()

SYSTEM_PROMPT = """You are the AI Assistant for the Workforce Intelligence Platform.
You have access to backend system tools to query projects, tasks, and employees.
Always use tools when you need to view or modify live platform data.
If an action requires multiple steps (such as looking up information before performing an action), execute them sequentially."""

ALLOWED_TOOL_NAMES = {
                "get_me_auth_me_get",
                "list_employees_employees",
                "get_employee_employees",
                "get_employee_skills_employees",
                "get_employee_workload_employees",
                "get_employee_availability_employees",

                "list_projects_projects",
                "get_project_projects",

                "list_tasks_for_project_tasks_project",
                "get_task_tasks",

                "get_recommendations_workflow_agent_recommendations_post",

                "list_assignments_assignments",
                "create_assignment_assignments",
                "approve_assignment_assignments_approve_post",
                "reject_assignment_assignments_reject_post",
                }

class WorkforceChatAssistant:
    def __init__(self, user_id: int = 1, role: str = "manager"):
        self.token = create_access_token(user_id=user_id, role=role)
        self.mcp = FastMCP.from_fastapi(
            app=app,
            httpx_client_kwargs={"headers": {"Authorization": f"Bearer {self.token}"}}
        )
        
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0,
            max_tokens=1000,
            max_retries=2,
            api_key=os.getenv("GROQ_API_KEY")
        )
        self.history = InMemoryChatMessageHistory()
        self.history.add_message(SystemMessage(content=SYSTEM_PROMPT))

    def get_recent_history(self, max_messages=10):

        messages = self.history.messages

        if len(messages) <= max_messages:
            return messages

        # Keep system prompt + latest messages
        return [messages[0]] + messages[-(max_messages - 1):]


    async def chat(self, user_input: str) -> str:
        # 1. Check the incoming message with the safety LLM
        decision = await check_safety(user_input)

        print("SAFETY CHECK:", user_input)
        print("SAFETY DECISION:", decision.decision)
        
        # 2. Block unsafe requests
        if decision.decision == "block":
            return f"Request blocked: {decision.reason}"

        # 3. Stop requests that need review
        if decision.decision == "review":
            return f"Request needs review: {decision.reason}"
        
        self.history.add_message(HumanMessage(content=user_input))

        async with Client(self.mcp) as client:
            # 1. Fetch available tools from FastMCP
            mcp_tools = await client.list_tools()

            mcp_tools = [tool for tool in mcp_tools if tool.name in ALLOWED_TOOL_NAMES]
            
            # FIX: Read .input_schema directly to prevent FastMCPDeprecationWarning
            formatted_tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                    }
                    for tool in mcp_tools
                    ]
            
            llm_with_tools = self.llm.bind_tools(formatted_tools)

            # 2. Multi-step autonomous tool execution loop (max 5 iterations per turn)
            for step in range(5):
                recent_history = self.get_recent_history(
                    max_messages=5
                )

                response = await llm_with_tools.ainvoke(recent_history)
                self.history.add_message(response)

                # If the LLM has formulated a text response without requesting tool calls, finish
                if not response.tool_calls:
                    return response.content

                # Execute every tool requested in this turn
                for tool_call in response.tool_calls:
                    tool_name = tool_call["name"]
                    tool_args = tool_call["args"]

                    try:
                        tool_res = await client.call_tool(tool_name, tool_args)
                        content_str = str(tool_res.data)
                    except Exception as e:
                        content_str = f"Tool execution error: {str(e)}"

                    self.history.add_message(
                        ToolMessage(
                            tool_call_id=tool_call["id"],
                            name=tool_name,
                            content=content_str
                        )
                    )

            # Return the latest response if loop finishes
            return self.history.messages[-1].content