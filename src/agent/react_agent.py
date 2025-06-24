import re
from typing import Callable, Dict, List

from pydantic import BaseModel

from src.tools.base import Tool, execute_tool


class ReActAgent:
    """Minimal implementation of the ReAct loop."""

    ACTION_RE = re.compile(r"^行動:\s*(\w+):\s*(.*)$", re.MULTILINE)
    FINAL_RE = re.compile(r"^最終的な答え:\s*(.*)$", re.MULTILINE)

    PROMPT_TEMPLATE = (
        "あなたは質問に答えるアシスタントです。\n"
        "利用可能な行動:\n{tools}\n\n"
        "質問: {input}\n"
        "{agent_scratchpad}"
    )

    def __init__(self, llm: Callable[[str], str], tools: List[Tool]):
        self.llm = llm
        self.tools = {t.name: t for t in tools}

    def tool_descriptions(self) -> str:
        descs = []
        for t in self.tools.values():
            descs.append(f"- {t.name}: {t.description}")
        return "\n".join(descs)

    def run(self, question: str, max_turns: int = 5) -> str:
        scratchpad = ""
        for _ in range(max_turns):
            prompt = self.PROMPT_TEMPLATE.format(
                input=question,
                tools=self.tool_descriptions(),
                agent_scratchpad=scratchpad,
            )
            output = self.llm(prompt)
            final_match = self.FINAL_RE.search(output)
            if final_match:
                return final_match.group(1)
            action_match = self.ACTION_RE.search(output)
            if not action_match:
                return "エラー: 行動を特定できませんでした"
            tool_name, tool_input = action_match.groups()
            observation = execute_tool(tool_name, {"url": tool_input}, self.tools)
            scratchpad += f"{output}\n観察: {observation}\n"
        return "エラー: 最大試行回数に達しました"
