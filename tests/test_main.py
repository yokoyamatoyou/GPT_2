import logging
from src import main as src_main


def test_parse_args():
    args = src_main.parse_args(['--memory', 'vector'])
    assert args.memory == 'vector'

def test_parse_args_memory_file():
    args = src_main.parse_args(['--memory-file', 'mem.json'])
    assert args.memory_file == 'mem.json'


def test_parse_args_log_file():
    args = src_main.parse_args(['--log-file', 'a.log'])
    assert args.log_file == 'a.log'

def test_parse_args_verbose():
    args = src_main.parse_args(['--verbose'])
    assert args.verbose

def test_parse_args_stream():
    args = src_main.parse_args(['--stream'])
    assert args.stream


def test_parse_args_list_tools():
    args = src_main.parse_args(['--list-tools'])
    assert args.list_tools

def test_parse_args_tot_options():
    args = src_main.parse_args(['--agent', 'tot', '--depth', '5', '--breadth', '6'])
    assert args.agent == 'tot'
    assert args.depth == 5
    assert args.breadth == 6


def test_parse_args_tot_env(monkeypatch):
    monkeypatch.setenv('TOT_DEPTH', '7')
    monkeypatch.setenv('TOT_BREADTH', '8')
    args = src_main.parse_args(['--agent', 'tot'])
    assert args.depth == 7
    assert args.breadth == 8


def test_parse_args_tot_env_validation(monkeypatch):
    import pytest
    monkeypatch.setenv('TOT_DEPTH', '0')
    with pytest.raises(SystemExit):
        src_main.parse_args(['--agent', 'tot'])
    monkeypatch.setenv('TOT_DEPTH', '2')
    monkeypatch.setenv('TOT_BREADTH', '-1')
    with pytest.raises(SystemExit):
        src_main.parse_args(['--agent', 'tot'])


def test_parse_args_tot_env_ignored_for_react(monkeypatch):
    monkeypatch.setenv('TOT_DEPTH', '0')
    monkeypatch.setenv('TOT_BREADTH', '0')
    # Should not raise SystemExit because the default agent is react
    args = src_main.parse_args([])
    assert args.agent == 'react'
    assert args.depth == 2
    assert args.breadth == 2


def test_parse_args_tot_option_validation():
    import pytest
    with pytest.raises(SystemExit):
        src_main.parse_args(['--agent', 'tot', '--depth', '0'])
    with pytest.raises(SystemExit):
        src_main.parse_args(['--agent', 'tot', '--breadth', '-1'])


def test_main_uses_vector_memory(monkeypatch):
    created = {}

    class DummyAgent:
        def __init__(self, llm, tools, memory, verbose=False):
            created['memory'] = memory
        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', lambda **k: None)
    monkeypatch.setattr(src_main, 'get_default_tools', lambda: [None, None])
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
        def __init__(self, llm, tools, memory, verbose=False):
            self.memory = memory
        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', lambda **k: None)
    monkeypatch.setattr(src_main, 'get_default_tools', lambda: [None, None])
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
        def __init__(self, llm, evaluate, *, max_depth, breadth, memory=None):
            created['called'] = True
            created['depth'] = max_depth
            created['breadth'] = breadth
        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ToTAgent', DummyTot)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'create_evaluator', lambda llm: lambda h: 1.0)
    monkeypatch.setattr(src_main, 'setup_logging', lambda **k: None)
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--agent', 'tot', '--depth', '3', '--breadth', '4'])

    assert created.get('called', False)
    assert created['depth'] == 3
    assert created['breadth'] == 4


def test_main_tot_loads_and_saves_memory(tmp_path, monkeypatch):
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

    class DummyTot:
        def __init__(self, llm, evaluate, *, max_depth, breadth, memory=None):
            self.memory = memory

        def run(self, q):
            return 'ok'

    monkeypatch.setattr(src_main, 'ToTAgent', DummyTot)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'create_evaluator', lambda llm: lambda h: 1.0)
    monkeypatch.setattr(src_main, 'setup_logging', lambda **k: None)
    monkeypatch.setattr(src_main, 'ConversationMemory', DummyMemory)
    monkeypatch.setattr(src_main, 'VectorMemory', DummyMemory)
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--agent', 'tot', '--memory-file', str(mem_file)])

    assert loaded['val']
    assert saved['val']


def test_main_passes_log_file(monkeypatch):
    captured = {}

    class DummyAgent:
        def __init__(self, llm, tools, memory, verbose=False):
            pass
        def run(self, q):
            return 'ok'

    def fake_setup_logging(level=logging.INFO, log_file=None):
        captured['file'] = log_file
        captured['level'] = level

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', fake_setup_logging)
    monkeypatch.setattr(src_main, 'get_default_tools', lambda: [None, None])
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--log-file', 'out.log'])

    assert captured['file'] == 'out.log'


def test_main_verbose(monkeypatch):
    captured = {}

    class DummyAgent:
        def __init__(self, llm, tools, memory, verbose=False):
            captured['verbose'] = verbose
        def run(self, q):
            return 'ok'

    def fake_setup_logging(level=logging.INFO, log_file=None):
        captured['level'] = level

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', fake_setup_logging)
    monkeypatch.setattr(src_main, 'get_default_tools', lambda: [None, None])
    monkeypatch.setattr('builtins.input', lambda prompt='': '')
    monkeypatch.setattr('builtins.print', lambda *a, **k: None)

    src_main.main(['--verbose'])

    assert captured['verbose'] is True
    assert captured['level'] == logging.DEBUG


def test_main_stream(monkeypatch):
    printed = []

    class DummyAgent:
        def __init__(self, llm, tools, memory, verbose=False):
            pass

        def run_iter(self, q):
            yield "step1"
            yield "step2"

    monkeypatch.setattr(src_main, 'ReActAgent', DummyAgent)
    monkeypatch.setattr(src_main, 'create_llm', lambda log_usage=True: lambda p: 'x')
    monkeypatch.setattr(src_main, 'setup_logging', lambda **k: None)
    monkeypatch.setattr(src_main, 'get_default_tools', lambda: [None, None])

    inputs = iter(["hi", ""]) 
    monkeypatch.setattr('builtins.input', lambda prompt='': next(inputs))
    monkeypatch.setattr('builtins.print', lambda *a, **k: printed.append(' '.join(map(str, a))))

    src_main.main(['--stream'])

    assert 'step1' in printed
    assert 'step2' in printed


def test_main_list_tools(monkeypatch):
    out = []
    monkeypatch.setattr('builtins.print', lambda *a, **k: out.append(' '.join(map(str, a))))

    src_main.main(['--list-tools'])

    assert any('web_scraper' in line for line in out)
    assert any('sqlite_query' in line for line in out)

