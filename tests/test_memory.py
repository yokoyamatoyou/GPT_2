from src.memory import ConversationMemory


def test_memory_save_load(tmp_path):
    mem = ConversationMemory()
    mem.add("user", "hello")
    mem.add("assistant", "hi")
    file = tmp_path / "conv.json"
    mem.save(file)

    other = ConversationMemory()
    other.load(file)
    assert other.messages == mem.messages


def test_save_creates_directory(tmp_path):
    mem = ConversationMemory()
    mem.add("user", "hi")
    file = tmp_path / "nested" / "conv.json"
    mem.save(file)
    assert file.exists()
