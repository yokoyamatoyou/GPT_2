from types import SimpleNamespace
import queue
from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.response_queue = queue.Queue()
    c.simple_llm = lambda prompt: ""
    c.agent_tools = []
    c.memory = None
    c.messages = []
    return c


def test_run_agent_uses_tot_env(monkeypatch):
    client = _client()
    created = {}

    def dummy_tot(llm, evaluate, *, max_depth, breadth, memory=None):
        created["depth"] = max_depth
        created["breadth"] = breadth
        return SimpleNamespace(run_iter=lambda q: [])

    monkeypatch.setattr(GPT, "ToTAgent", dummy_tot)
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_DEPTH", "3")
    monkeypatch.setenv("TOT_BREADTH", "4")

    client.run_agent("tot", "q")

    assert created["depth"] == 3
    assert created["breadth"] == 4


def test_run_agent_invalid_tot_env(monkeypatch):
    client = _client()

    monkeypatch.setattr(GPT, "ToTAgent", lambda *a, **k: SimpleNamespace(run_iter=lambda q: []))
    monkeypatch.setattr(GPT, "create_evaluator", lambda llm: None)
    monkeypatch.setenv("TOT_DEPTH", "0")

    client.run_agent("tot", "q")
    outputs = []
    while not client.response_queue.empty():
        outputs.append(client.response_queue.get())
    assert any("エラー" in o for o in outputs)
