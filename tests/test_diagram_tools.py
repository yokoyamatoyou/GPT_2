import os
from graphviz import Source
from mermaid import Mermaid

from src.tools.graphviz_tool import create_graphviz_diagram
from src.tools.mermaid_tool import create_mermaid_diagram


def test_create_graphviz_diagram_success(monkeypatch, tmp_path):
    def fake_render(self, filename, cleanup=True):
        open(filename, "wb").close()
        return filename

    monkeypatch.setattr(Source, "render", fake_render)
    path = create_graphviz_diagram("digraph {a->b}")
    assert path.endswith(".png")
    assert os.path.isfile(path)
    os.unlink(path)


def test_create_graphviz_diagram_failure(monkeypatch):
    def fake_render(self, filename, cleanup=True):
        raise RuntimeError("boom")

    monkeypatch.setattr(Source, "render", fake_render)
    result = create_graphviz_diagram("digraph {}")
    assert result.startswith("Failed to generate diagram")


def test_create_mermaid_diagram_success(monkeypatch):
    def fake_png(self, filename):
        open(filename, "wb").close()

    monkeypatch.setattr(Mermaid, "to_png", fake_png)
    path = create_mermaid_diagram("graph TD; A-->B;")
    assert path.endswith(".png")
    assert os.path.isfile(path)
    os.unlink(path)


def test_create_mermaid_diagram_failure(monkeypatch):
    def fake_png(self, filename):
        raise RuntimeError("fail")

    monkeypatch.setattr(Mermaid, "to_png", fake_png)
    result = create_mermaid_diagram("graph TD;")
    assert result.startswith("Failed to generate diagram")
