"""
DARKWIN — Unit Tests | Console Progress Renderer
"""

import io

from unittest.mock import patch


def _clear_listeners():
    from core import progress as hub
    hub._listeners = []


def test_non_tty_prints_percentage_lines(capsys):
    from core import progress as hub
    from core.console_progress import cli_progress

    _clear_listeners()
    hub.reset()
    with cli_progress("scan"):
        hub.advance(25, "checking hosts")
        hub.set_pct(100, "done")

    out = capsys.readouterr().out
    assert "[ 25%] checking hosts" in out
    assert "[100%] done" in out
    assert hub._listeners == []


def test_tty_renders_live_bar(monkeypatch):
    from core import progress as hub
    from core import console_progress as cp

    _clear_listeners()
    hub.reset()
    buf = io.StringIO()
    fake = cp.Console(file=buf, force_terminal=True, width=80)
    monkeypatch.setattr(cp, "Console", lambda file=None: fake)

    with cp.cli_progress("scan"):
        hub.advance(42, "parsing js")

    import re
    out = re.sub(r"\x1b\[[0-9;]*m", "", buf.getvalue())
    out = out.replace("\x1b[?25l", "").replace("\x1b[?25h", "")
    # rich's Live redraws via carriage return, so only the latest frame is
    # retained in a capture — verify the bar rendered and completed at 100%.
    assert "100%" in out
    assert "Scan complete" in out
    assert hub._listeners == []


def test_cleans_listener_on_exception():
    from core import progress as hub
    from core.console_progress import cli_progress

    _clear_listeners()
    hub.reset()
    try:
        with cli_progress("scan"):
            hub.advance(10, "x")
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    assert hub._listeners == []