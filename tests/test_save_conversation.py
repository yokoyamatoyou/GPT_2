import json
import os
from types import SimpleNamespace

import GPT

ChatGPTClient = GPT.ChatGPTClient


def _client():
    return ChatGPTClient.__new__(ChatGPTClient)


def test_save_conversation(tmp_path, monkeypatch):
    client = _client()
    client.current_title = "TestChat"
    client.model_var = SimpleNamespace(get=lambda: "model-x")
    client.messages = [{"role": "user", "content": "hi"}]
    client.uploaded_files = [{"name": "file.docx", "type": ".docx"}]

    monkeypatch.chdir(tmp_path)
    client.save_conversation()

    conv_dir = tmp_path / "conversations"
    files = list(conv_dir.glob("*.json"))
    assert len(files) == 1

    with open(files[0], "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["title"] == "TestChat"
    assert data["model"] == "model-x"
    assert data["messages"] == client.messages
    assert data["uploaded_files_metadata"] == [{"name": "file.docx", "type": ".docx"}]
    assert "timestamp" in data
