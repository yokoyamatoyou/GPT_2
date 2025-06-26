import os
import subprocess

from src.tools.graphviz_tool import create_graphviz_diagram
from src.tools.mermaid_tool import create_mermaid_diagram


def test_create_graphviz_diagram_success(monkeypatch):
    def mock_run(cmd, check, stdout, stderr):
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", mock_run)
    path = create_graphviz_diagram("digraph {a->b}")
    assert path.endswith(".png")
    assert os.path.isfile(path)
    os.unlink(path)


def test_create_graphviz_diagram_missing_cli(monkeypatch):
    def mock_run(cmd, check, stdout, stderr):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = create_graphviz_diagram("digraph {}")
    assert result == "graphviz 'dot' command not found."


def test_create_mermaid_diagram_success(monkeypatch):
    def mock_run(cmd, check, stdout, stderr):
        return subprocess.CompletedProcess(cmd, 0, b"", b"")

    monkeypatch.setattr(subprocess, "run", mock_run)
    path = create_mermaid_diagram("graph TD; A-->B;")
    assert path.endswith(".png")
    assert os.path.isfile(path)
    os.unlink(path)


def test_create_mermaid_diagram_missing_cli(monkeypatch):
    def mock_run(cmd, check, stdout, stderr):
        raise FileNotFoundError

    monkeypatch.setattr(subprocess, "run", mock_run)
    result = create_mermaid_diagram("graph TD;")
    assert result == "mmdc command not found. Install @mermaid-js/mermaid-cli."
