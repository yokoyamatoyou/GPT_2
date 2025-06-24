from dataclasses import dataclass
from typing import Callable, Type

from pydantic import BaseModel


@dataclass
class Tool:
    """Simple container for tool definitions."""

    name: str
    description: str
    func: Callable
    args_schema: Type[BaseModel]


def execute_tool(name: str, args: dict, tools: dict):
    tool = tools.get(name)
    if not tool:
        return f"Unknown tool: {name}"
    try:
        parsed = tool.args_schema(**args)
    except Exception as e:
        return f"Invalid arguments for {name}: {e}"
    return tool.func(**parsed.model_dump())
