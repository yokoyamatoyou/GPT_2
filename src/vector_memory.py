from dataclasses import dataclass, field
from typing import List, Dict
import json

from .memory import BaseMemory

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class VectorMemory(BaseMemory):
    """Conversation memory backed by a simple vector store using TF-IDF."""

    messages: List[Dict[str, str]] = field(default_factory=list)

    def add(self, role: str, content: str) -> None:
        """Add a message to memory."""
        self.messages.append({"role": role, "content": content})

    def search(self, query: str, top_k: int = 3) -> List[str]:
        """Return the contents of the messages most similar to the query."""
        corpus = [m["content"] for m in self.messages]
        if not corpus:
            return []
        vectorizer = TfidfVectorizer()
        vectors = vectorizer.fit_transform(corpus + [query])
        sims = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
        indices = sims.argsort()[::-1][:top_k]
        return [corpus[i] for i in indices]

    def save(self, path: str) -> None:
        """Persist messages to a JSON file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"messages": self.messages}, f, ensure_ascii=False, indent=2)

    def load(self, path: str) -> None:
        """Load messages from a JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.messages = data.get("messages", [])
