from dataclasses import dataclass, field
from typing import List, Dict, Protocol
import json


class BaseMemory(Protocol):
    """Protocol for memory implementations."""

    messages: List[Dict[str, str]]

    def add(self, role: str, content: str) -> None:
        ...

    def save(self, path: str) -> None:
        ...

    def load(self, path: str) -> None:
        ...

    def search(self, query: str, top_k: int = 3) -> List[str]:
        ...

@dataclass
class ConversationMemory:
    """Simple in-memory store for conversation messages."""

    messages: List[Dict[str, str]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        """Add a message to memory."""
        self.messages.append({"role": role, "content": content})

    def save(self, path: str) -> None:
        """Persist messages to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"messages": self.messages}, f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        """Load messages from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data.get("messages", [])

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Return messages containing the query text."""
        results = [m["content"] for m in self.messages if query in m["content"]]
        return results[:top_k]
