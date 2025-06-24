from __future__ import annotations

import os
from dotenv import load_dotenv
from openai import OpenAI

from src.agent import ReActAgent
from src.tools.web_scraper import get_tool
from src.memory import ConversationMemory


def create_llm() -> callable:
    """Create an OpenAI completion callable."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    client = OpenAI(api_key=api_key)

    def llm(prompt: str) -> str:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content

    return llm


def main() -> None:
    llm = create_llm()
    memory = ConversationMemory()
    agent = ReActAgent(llm, [get_tool()], memory)

    print("Enter an empty line to quit.")
    while True:
        question = input("質問: ").strip()
        if not question:
            break
        answer = agent.run(question)
        print(f"答え: {answer}")


if __name__ == "__main__":
    main()
