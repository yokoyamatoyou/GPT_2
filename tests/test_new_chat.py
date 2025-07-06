from types import SimpleNamespace

from src.ui import main as GPT
from src.memory import ConversationMemory

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.memory = ConversationMemory()
    c.memory.add("user", "hi")
    c.chat_display = SimpleNamespace(configure=lambda *a, **k: None,
                                     delete=lambda *a, **k: None,
                                     insert=lambda *a, **k: None)
    c.file_list_text = SimpleNamespace(configure=lambda *a, **k: None,
                                       delete=lambda *a, **k: None)
    c.window = SimpleNamespace(title=lambda *a, **k: None)
    return c


def test_new_chat_clears_memory():
    client = _client()
    assert client.memory.messages
    client.new_chat()
    assert client.memory.messages == []
