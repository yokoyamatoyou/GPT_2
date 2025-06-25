import types
import json
from src import main as src_main


def test_parse_args():
    args = src_main.parse_args(['--memory', 'vector'])
    assert args.memory == 'vector'

def test_parse_args_memory_file():
    args = src_main.parse_args(['--memory-file', 'mem.json'])
    assert args.memory_file == 'mem.json'


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


def test_main_loads_and_saves_memory(tmp_path, monkeypatch):
    mem_file = tmp_path / 'mem.json'
    mem_file.write_text('{"messages": []}', encoding='utf-8')

    loaded = {'val': False}
    saved = {'val': False}

    class DummyMemory(src_main.ConversationMemory):
        def load(self, path: str) -> None:
            loaded['val'] = True
            super().load(path)

        def save(self, path: str) -> None:
            saved['val'] = True
            super().save(path)

    class DummyAgent:
        def __init__(self, llm, tools, memory):
            self.memory = memory
        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', lambda: None)
    monkeypatch.setattr(src_main, 'get_web_scraper', lambda: None)
    monkeypatch.setattr(src_main, 'get_sqlite_tool', lambda: None)
    monkeypatch.setattr(src_main, 'ConversationMemory', DummyMemory)
    monkeypatch.setattr(src_main, 'VectorMemory', DummyMemory)
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--memory-file', str(mem_file)])

    assert loaded['val']
    assert saved['val']


def test_main_uses_tot_agent(monkeypatch):
    created = {}

    class DummyTot:
        def __init__(self, llm, evaluate):
            created['called'] = True
        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ToTAgent', DummyTot)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'create_evaluator', lambda llm: lambda h: 1.0)
    monkeypatch.setattr(src_main, 'setup_logging', lambda: None)
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--agent', 'tot'])

    assert created.get('called', False)

