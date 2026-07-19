"""
DARKWIN — Unit Tests | Engine
"""

import pytest
from pathlib import Path


def test_run_command_returns_zero_on_success(tmp_path):
    from core.engine import run_command
    log_file = str(tmp_path / "test.log")
    exit_code = run_command("echo hello", log_file=log_file, tool_name="test", target="localhost")
    assert exit_code == 0


def test_run_command_writes_output_to_log(tmp_path):
    from core.engine import run_command
    log_file = str(tmp_path / "output.log")
    run_command("echo darkwin_test_marker", log_file=log_file, tool_name="test", target="localhost")
    content = Path(log_file).read_text(encoding="utf-8")
    assert "darkwin_test_marker" in content


def test_run_command_returns_nonzero_on_failure(tmp_path):
    from core.engine import run_command
    log_file = str(tmp_path / "fail.log")
    exit_code = run_command("exit 1", log_file=log_file, tool_name="test", target="localhost")
    assert exit_code != 0


def test_run_parallel_returns_list(tmp_path):
    from core.engine import run_parallel
    commands = [
        {"cmd": "echo a", "log_file": str(tmp_path / "a.log"), "tool_name": "test", "target": "t"},
        {"cmd": "echo b", "log_file": str(tmp_path / "b.log"), "tool_name": "test", "target": "t"},
    ]
    results = run_parallel(commands, max_workers=2)
    assert isinstance(results, list)
    assert len(results) == 2
    assert all(r == 0 for r in results)
