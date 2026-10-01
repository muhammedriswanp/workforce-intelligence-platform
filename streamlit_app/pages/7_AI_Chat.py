import sys
import asyncio
from pathlib import Path

import streamlit as st

from ui import apply_theme, page_header, render_sidebar, require_role

st.set_page_config(page_title="AI Chat", layout="wide")
apply_theme()
render_sidebar()
require_role("manager")


def _project_root():
    starting = Path(__file__).resolve()
    folders = list(starting.parents) + [Path.cwd().resolve()] + list(Path.cwd().resolve().parents)
    for folder in folders:
        if (folder / "main.py").exists() and (folder / "app").is_dir():
            return folder
    raise RuntimeError("Could not locate the project root (no main.py next to an app/ directory).")


if str(_project_root()) not in sys.path:
    sys.path.insert(0, str(_project_root()))

from app.chat.assistant import SYSTEM_PROMPT, WorkforceChatAssistant  # noqa: E402
from fastmcp.client import Client  # noqa: E402
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage  # noqa: E402

MAX_STEPS = 5

page_header("🤖", "AI Chat", "Ask about projects, tasks, employees, skills and assignments")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [SystemMessage(content=SYSTEM_PROMPT)]

history = st.session_state.chat_history


@st.cache_resource
def get_bot(user_id, role):
    return WorkforceChatAssistant(user_id=user_id, role=role)


bot = get_bot(st.session_state.get("user_id") or 0, st.session_state.get("role") or "manager")
bot.history = history


async def stream_reply(bot, user_input, sink):
    """Stream one assistant turn token by token, running tools between LLM steps.

    Mirrors the loop in WorkforceChatAssistant.chat() but uses astream() so the
    UI can render text as it is produced. Text is accumulated separately from the
    tool markers so the stored history stays clean.
    """
    history = bot.history
    history.append(HumanMessage(content=user_input))
    sink["text"] = ""

    async with Client(bot.mcp) as client:
        mcp_tools = await client.list_tools()
        formatted_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.input_schema,
                },
            }
            for tool in mcp_tools
        ]
        llm_with_tools = bot.llm.bind_tools(formatted_tools)

        for _ in range(MAX_STEPS):
            merged = None
            async for chunk in llm_with_tools.astream(history):
                merged = chunk if merged is None else merged + chunk
                if chunk.content:
                    sink["text"] += chunk.content
                    yield chunk.content

            if merged is None:
                break

            history.append(merged)

            if not merged.tool_calls:
                return

            for tool_call in merged.tool_calls:
                tool_name = tool_call["name"]
                try:
                    tool_res = await client.call_tool(tool_name, tool_call["args"])
                    content_str = str(tool_res.data)
                except Exception as exc:
                    content_str = f"Tool execution error: {exc}"

                history.append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        name=tool_name,
                        content=content_str,
                    )
                )


with st.sidebar:
    st.markdown('<div class="side-head">Conversation</div>', unsafe_allow_html=True)
    st.caption(f"{max(0, sum(1 for m in history[1:] if getattr(m, 'type', None) != 'tool' and str(getattr(m, 'content', '') or '').strip()))} messages this session")
    if st.button("Clear conversation", use_container_width=True, key="chat_clear"):
        st.session_state.chat_history = [SystemMessage(content=SYSTEM_PROMPT)]
        st.rerun()

AVATARS = {
    "human": "user",
    "ai": "assistant",
    "AIMessageChunk": "assistant",
    "system": "assistant",
}

if chat_error := st.session_state.pop("chat_error", None):
    st.error(chat_error)

for message in history[1:]:
    if getattr(message, "type", None) == "tool":
        continue
    content = str(getattr(message, "content", "") or "").strip()
    if not content:
        continue
    with st.chat_message(AVATARS.get(getattr(message, "type", "ai"), "assistant")):
        st.markdown(content)

if prompt := st.chat_input("Ask about your workforce data…"):
    turn_start = len(history)
    with st.chat_message("user"):
        st.markdown(prompt)

    sink = {}
    with st.chat_message("assistant"):
        try:
            st.write_stream(stream_reply(bot, prompt, sink))
        except Exception as exc:
            del history[turn_start:]
            st.session_state.chat_error = f"The assistant could not complete that request: {exc}"
            st.rerun()

    st.rerun()
