import queue
from types import SimpleNamespace

from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.response_queue = queue.Queue()
    c.messages = [{"role": "user", "content": "hi"}]
    c.model_var = SimpleNamespace(get=lambda: "m")
    c.temp_slider = SimpleNamespace(get=lambda: 0.0)
    return c


def test_get_response_stream(monkeypatch):
    client = _client()

    def create(model, messages, temperature, stream=True):
        assert stream
        parts = [
            "Hello",
            " world",
            None,
        ]
        return [
            SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content=p))])
            for p in parts
        ]

    client.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

    client.get_response()

    outputs = []
    while not client.response_queue.empty():
        outputs.append(client.response_queue.get())

    assert outputs == [
        "🤖 Assistant: ",
        "Hello",
        " world",
        "\n",
        "__SAVE__",
    ]
