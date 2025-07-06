import queue
import logging
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
        return [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content="Hello"), finish_reason=None
                    )
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content=" world"), finish_reason=None
                    )
                ]
            ),
            SimpleNamespace(
                choices=[
                    SimpleNamespace(delta=SimpleNamespace(content=None), finish_reason="stop")
                ]
            ),
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


def test_generate_title_logs_error(caplog):
    client = ChatGPTClient.__new__(ChatGPTClient)
    client.window = SimpleNamespace(title=lambda *a, **k: None)

    def raise_err(*a, **k):
        raise RuntimeError("boom")

    client.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=raise_err))
    )

    caplog.set_level(logging.ERROR)
    client.generate_title("hi")

    assert "boom" in caplog.text
    assert client.current_title


def test_get_response_tool_calls(monkeypatch):
    client = _client()

    call = {"count": 0}

    def create(model, messages, temperature, stream=True, tools=None, tool_choice=None):
        call["count"] += 1
        if call["count"] == 1:
            tc = SimpleNamespace(
                id="1",
                function=SimpleNamespace(
                    name="create_graphviz_diagram",
                    arguments='{"code": "digraph {a->b}"}'
                ),
            )
            return [
                SimpleNamespace(
                    choices=[
                        SimpleNamespace(
                            delta=SimpleNamespace(tool_calls=[tc]),
                            finish_reason="tool_calls",
                        )
                    ]
                )
            ]
        parts = ["done", None]
        return [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content=p),
                        finish_reason=None if p else "stop",
                    )
                ]
            )
            for p in parts
        ]

    client.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    client.tool_funcs = {"create_graphviz_diagram": lambda code: "/tmp/x.png"}
    client.tools = [{"type": "function", "function": {"name": "create_graphviz_diagram"}}]

    client.get_response()

    out = []
    while not client.response_queue.empty():
        out.append(client.response_queue.get())

    assert out[0] == "🤖 Assistant: "
    assert "done" in "".join(out)
    assert client.messages[1]["role"] == "assistant"
    assert client.messages[2]["role"] == "tool"
    assert client.messages[2]["content"] == "/tmp/x.png"
    assert client.messages[-1]["role"] == "assistant"
    assert client.messages[-1]["content"] == "done"
