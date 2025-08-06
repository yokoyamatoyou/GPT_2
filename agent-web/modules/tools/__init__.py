from typing import List
from .web_scraper import get_tool as get_web_scraper
from .sqlite_tool import get_tool as get_sqlite_tool
from .mermaid_tool import get_tool as get_mermaid_tool
from .graphviz_tool import get_tool as get_graphviz_tool
from .base import Tool, execute_tool

# Map the new tool names from the UI to the old tool creation functions
TOOL_MAPPING = {
    "web_search": get_web_scraper,
    "sql_query": get_sqlite_tool,
    "diagram": get_graphviz_tool, # Defaulting 'diagram' to graphviz
}

def get_tools_by_name(tool_names: List[str]) -> List[Tool]:
    """
    Returns a list of Tool objects for the given tool names.
    """
    tools = []
    for name in tool_names:
        if name in TOOL_MAPPING:
            tools.append(TOOL_MAPPING[name]())
    return tools


__all__ = [
    "get_tools_by_name",
    "Tool",
    "execute_tool",
]
