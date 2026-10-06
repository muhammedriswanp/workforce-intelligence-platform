import sys
import asyncio
import concurrent.futures
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
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # noqa: E402

page_header("🤖", "AI Chat", "Ask about projects, tasks, employees, skills and assignments")


def _run_async(coro):
    """Run WorkforceChatAssistant.chat() from Streamlit's synchronous script."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        return pool.submit(asyncio.run, coro).result()


_bot_key = (st.session_state.get("user_id"), st.session_state.get("role"))
if "chat_bot" not in st.session_state or st.session_state.get("chat_bot_key") != _bot_key:
    st.session_state.chat_bot = WorkforceChatAssistant(
        user_id=st.session_state.get("user_id") or 1,
        role=st.session_state.get("role") or "manager",
    )
    st.session_state.chat_bot_key = _bot_key

bot = st.session_state.chat_bot
history = bot.history


with st.sidebar:
    st.markdown('<div class="side-head">Conversation</div>', unsafe_allow_html=True)
    st.caption(
        f"{max(0, sum(1 for m in history.messages if getattr(m, 'type', None) not in ('system', 'tool') and str(getattr(m, 'content', '') or '').strip()))} messages this session"
    )
    if st.button("Clear conversation", use_container_width=True, key="chat_clear"):
        history.clear()
        history.add_message(SystemMessage(content=SYSTEM_PROMPT))
        st.rerun()

AVATARS = {
    "human": "user",
    "ai": "assistant",
    "AIMessageChunk": "assistant",
    "system": "assistant",
}

if chat_error := st.session_state.pop("chat_error", None):
    st.error(chat_error)

for message in history.messages:
    message_type = getattr(message, "type", None)
    if message_type in ("system", "tool"):
        continue
    content = str(getattr(message, "content", "") or "").strip()
    if not content:
        continue
    with st.chat_message(AVATARS.get(message_type, "assistant")):
        st.markdown(content)

if prompt := st.chat_input("Ask about your workforce data…"):
    with st.chat_message("user"):
        st.markdown(prompt)

    turn_start = len(history.messages)
    with st.chat_message("assistant"):
        try:
            response = _run_async(bot.chat(prompt))
        except Exception as exc:
            history.messages[:] = history.messages[:turn_start]
            st.session_state.chat_error = f"The assistant could not complete that request: {exc}"
            st.rerun()
        else:
            if len(history.messages) == turn_start:
                # chat() returned early on block/review without recording the turn
                history.add_message(HumanMessage(content=prompt))
                history.add_message(AIMessage(content=str(response)))
            st.markdown(str(response))
