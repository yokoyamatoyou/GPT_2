import tkinter
from src.ui import main as GPT


def test_get_font_family_tclerror(monkeypatch):
    def raise_tclerror(*args, **kwargs):
        raise tkinter.TclError('no display')
    monkeypatch.setattr(tkinter, 'Tk', raise_tclerror)
    assert GPT.get_font_family() == "Helvetica"
