import asyncio
from app.chat.assistant import WorkforceChatAssistant

async def main():
    bot = WorkforceChatAssistant(user_id=1, role="manager")
    print("Workforce AI Chatbot Ready! (Type 'exit' to quit)\n" + "-"*50)

    while True:
        user_text = input("\nYou: ").strip()
        if not user_text:
            continue
        if user_text.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        reply = await bot.chat(user_text)
        print(f"\nAI: {reply}")

if __name__ == "__main__":
    asyncio.run(main())