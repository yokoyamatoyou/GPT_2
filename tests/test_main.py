import types
from src import main as src_main


def test_parse_args():
    args = src_main.parse_args(['--memory', 'vector'])
    assert args.memory == 'vector'


def test_main_uses_vector_memory(monkeypatch):
    created = {}

    class DummyAgent:
        def __init__(self, llm, tools, memory):
            created['memory'] = memory
        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', lambda: None)
    monkeypatch.setattr(src_main, 'get_web_scraper', lambda: None)
    monkeypatch.setattr(src_main, 'get_sqlite_tool', lambda: None)
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--memory', 'vector'])
    assert isinstance(created['memory'], src_main.VectorMemory)

