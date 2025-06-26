from __future__ import annotations

import argparse
import os
import logging
import sys
from dotenv import load_dotenv
from openai import OpenAI

from .logging_utils import setup_logging

from src.agent import ReActAgent, ToTAgent
from src.tools import get_web_scraper, get_sqlite_tool
from src.memory import ConversationMemory
from src.vector_memory import VectorMemory

logger = logging.getLogger(__name__)


def positive_int(value: str) -> int:
    """Return *value* as a positive ``int``.

    Raises ``argparse.ArgumentTypeError`` if ``value`` is not a positive
    integer.
    """
    ivalue = int(value)
    if ivalue < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return ivalue


def _read_tot_env() -> tuple[int | None, int | None]:
    """Return depth and breadth from environment variables if set."""
    depth = os.getenv("TOT_DEPTH")
    breadth = os.getenv("TOT_BREADTH")
    try:
        depth_val = positive_int(depth) if depth is not None else None
        breadth_val = positive_int(breadth) if breadth is not None else None
    except argparse.ArgumentTypeError as exc:  # pragma: no cover - just re-raise
        raise SystemExit(exc)
    return depth_val, breadth_val


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


def create_evaluator(llm: callable) -> callable:
    """Create an evaluation function for :class:`ToTAgent`."""

    def evaluate(history: str) -> float:
        prompt = (
            "以下の思考の有用性を0から1の数値で評価してください。数値のみ回答してください。\n"
            f"{history}\nスコア:"
        )
        resp = llm(prompt)
        try:
            return float(resp.strip())
        except Exception:
            logger.warning("Failed to parse evaluation score from '%s'", resp)
            return 0.0

    return evaluate


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(description="Run the simple agent")
    parser.add_argument(
        "--memory",
        choices=["conversation", "vector"],
        default="conversation",
        help="Type of memory store to use",
    )
    parser.add_argument(
        "--memory-file",
        help="Path to JSON file for persisting conversation memory",
    )
    parser.add_argument(
        "--agent",
        choices=["react", "tot"],
        default="react",
        help="Which agent implementation to use (tot is experimental)",
    )
    depth_default = 2
    breadth_default = 2

    parser.add_argument(
        "--depth",
        type=positive_int,
        default=depth_default,
        help="Max search depth for the ToT agent",
    )
    parser.add_argument(
        "--breadth",
        type=positive_int,
        default=breadth_default,
        help="Number of branches to keep at each depth for the ToT agent",
    )
    parser.add_argument(
        "--log-file",
        help="Write logs to the specified file (overrides AGENT_LOG_FILE)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging and verbose agent output",
    )
    parser.add_argument(
        "--stream",
        action="store_true",
        help="Print intermediate reasoning steps while running",
    )
    parsed = parser.parse_args(args)

    arg_list = args if args is not None else sys.argv[1:]
    if parsed.agent == "tot":
        if "--depth" not in arg_list or "--breadth" not in arg_list:
            try:
                depth_val, breadth_val = _read_tot_env()
            except SystemExit as exc:
                raise SystemExit(f"Invalid TOT_DEPTH/BREADTH: {exc}")
            if "--depth" not in arg_list and depth_val is not None:
                parsed.depth = depth_val
            if "--breadth" not in arg_list and breadth_val is not None:
                parsed.breadth = breadth_val

    return parsed


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level=level, log_file=args.log_file)
    llm = create_llm(log_usage=True)
    memory = None
    tools = None
    if args.agent == "react":
        memory = VectorMemory() if args.memory == "vector" else ConversationMemory()
        if args.memory_file and os.path.exists(args.memory_file):
            try:
                memory.load(args.memory_file)
            except Exception as exc:
                logger.warning(
                    "Failed to load memory file %s: %s", args.memory_file, exc
                )
        tools = [get_web_scraper(), get_sqlite_tool()]
        agent = ReActAgent(llm, tools, memory, verbose=args.verbose)
    else:
        evaluator = create_evaluator(llm)
        memory = VectorMemory() if args.memory == "vector" else ConversationMemory()
        if args.memory_file and os.path.exists(args.memory_file):
            try:
                memory.load(args.memory_file)
            except Exception as exc:
                logger.warning(
                    "Failed to load memory file %s: %s", args.memory_file, exc
                )
        agent = ToTAgent(
            llm,
            evaluator,
            max_depth=args.depth,
            breadth=args.breadth,
            memory=memory,
        )

    print("Enter an empty line to quit.")
    while True:
        question = input("質問: ").strip()
        if not question:
            break
        if args.stream:
            for step in agent.run_iter(question):
                print(step)
        else:
            answer = agent.run(question)
            print(f"答え: {answer}")
    if args.memory_file and memory is not None:
        try:
            memory.save(args.memory_file)
        except Exception as exc:
            logger.warning(
                "Failed to save memory file %s: %s", args.memory_file, exc
            )


if __name__ == "__main__":
    main(sys.argv[1:])
