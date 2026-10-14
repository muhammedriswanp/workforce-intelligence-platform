import os
import warnings

os.environ["LANGSMITH_TRACING"] = "false"
warnings.filterwarnings("ignore", message="Could not obtain an event loop")

import asyncio
import json
from pathlib import Path
import re
from app.chat.employee_assistant import EmployeeChatAssistant

EMPLOYEE_ID = 1  
PATH = Path(__file__).parent / "answer_set.json"


def clean(text: str) -> str:
    text = text.lower().replace("*", "")
    text = re.sub(r"[\u2010-\u2015\u00a0\u202f]", " ", text)
    text = text.replace("’", "'")
    return re.sub(r"\s+", " ", text)


def has_fact(answer: str, fact: str) -> bool:
    return any(option.strip() in answer for option in fact.split("|"))


async def main():
    items = json.loads(PATH.read_text(encoding="utf-8"))
    passed = 0

    for item in items:
        assistant = EmployeeChatAssistant(EMPLOYEE_ID)  # fresh history each time
        answer = await assistant.chat(item["question"])
        text = clean(answer)

        used_search = any(
            m.type == "tool" and m.name == "search_policies"
            for m in assistant.history.messages
        )
        missing = [f for f in item["facts"] if not has_fact(text, f)]
        ok = used_search and not missing
        passed += ok

        print(f"{item['id']:<3}{'PASS' if ok else 'FAIL':<6}{item['question']}")
        if not ok:
            print(f"     searched={used_search} missing={missing}")
            print(f"     answer: {answer[:200]}")

    print(f"\nPassed {passed}/{len(items)}")


if __name__ == "__main__":
    asyncio.run(main())