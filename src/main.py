from __future__ import annotations

import argparse
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

from .logging_utils import setup_logging

from src.agent import ReActAgent
from src.tools import get_web_scraper, get_sqlite_tool
from src.memory import ConversationMemory
from src.vector_memory import VectorMemory

logger = logging.getLogger(__name__)


def create_llm(*, log_usage: bool = False) -> callable:
    """Create an OpenAI completion callable.

    Parameters
    ----------
    log_usage: bool
        If True, token usage and estimated cost from the OpenAI API response
        will be logged.
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    token_price = float(os.getenv("OPENAI_TOKEN_PRICE", "0"))
    client = OpenAI(api_key=api_key)

    def llm(prompt: str) -> str:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
        )
        if log_usage and getattr(resp, "usage", None):
            try:
                total = resp.usage.total_tokens
            except Exception as exc:
                logger.warning("Failed to read token usage: %s", exc)
            else:
                cost = total * token_price
                logger.info("Tokens used: %s | Cost: $%.4f", total, cost)
        return resp.choices[0].message.content

    return llm


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="Run the simple ReAct agent")
    parser.add_argument(
        "--memory",
        choices=["conversation", "vector"],
        default="conversation",
        help="Type of memory store to use",
    )
    return parser.parse_args(args)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    setup_logging()
    llm = create_llm(log_usage=True)
    if args.memory == "vector":
        memory = VectorMemory()
    else:
        memory = ConversationMemory()
    tools = [get_web_scraper(), get_sqlite_tool()]
    agent = ReActAgent(llm, tools, memory)

    print("Enter an empty line to quit.")
    while True:
        question = input("質問: ").strip()
        if not question:
            break
        answer = agent.run(question)
        print(f"答え: {answer}")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
