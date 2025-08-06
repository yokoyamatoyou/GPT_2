from typing import List
from .react_agent import ReActAgent
from .tot_agent import ToTAgent
from .cot_agent import CoTAgent
from .presentation_agent import PresentationAgent
from ..utils.llm_client import LLMClient
from ..tools import get_tools_by_name

from ..memory.conversation_memory import BaseMemory

def get_agent(agent_name: str, llm_client: LLMClient, tool_names: List[str], memory: BaseMemory):
    """
    Factory function to get an agent instance by name.
    """
    if agent_name == "react":
        tools = get_tools_by_name(tool_names)
        return ReActAgent(llm_client=llm_client, tools=tools, memory=memory)
    elif agent_name == "cot":
        return CoTAgent(llm_client=llm_client, memory=memory)
    elif agent_name == "tot":
        return ToTAgent(llm_client=llm_client, memory=memory)
    else:
        # Fallback or error
        # For now, let's return a default agent
        tools = get_tools_by_name(tool_names)
        return ReActAgent(llm_client=llm_client, tools=tools)

__all__ = ["ReActAgent", "CoTAgent", "ToTAgent", "PresentationAgent", "get_agent"]
