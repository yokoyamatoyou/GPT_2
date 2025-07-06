from types import SimpleNamespace
from src.ui import main as GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    c = ChatGPTClient.__new__(ChatGPTClient)
    c.diagram_label = SimpleNamespace(configure=lambda **k: c.calls.setdefault('label', []).append(k), image=None)
    c.save_button = SimpleNamespace(configure=lambda **k: c.calls.setdefault('save', []).append(k))
    c.clear_button = SimpleNamespace(configure=lambda **k: c.calls.setdefault('clear', []).append(k))
    c.calls = {}
    return c


def test_display_and_clear_diagram(monkeypatch, tmp_path):
    client = _client()
    img = tmp_path / "d.png"
    img.write_bytes(b'x')
    monkeypatch.setattr(GPT.Image, 'open', lambda path: object())
    monkeypatch.setattr(GPT.ctk, 'CTkImage', lambda light_image, size: object())

    client.display_diagram(str(img))
    assert client._diagram_path == str(img)
    assert any(k.get('state') == 'normal' for k in client.calls.get('save', []))
    assert any(k.get('state') == 'normal' for k in client.calls.get('clear', []))

    client.calls = {'label': [], 'save': [], 'clear': []}
    client.clear_diagram()
    assert client._diagram_path is None
    assert any(k.get('state') == 'disabled' for k in client.calls.get('save', []))
    assert any(k.get('state') == 'disabled' for k in client.calls.get('clear', []))
