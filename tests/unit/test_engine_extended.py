"""
DARKWIN — Unit Tests | Engine (Extended)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_run_command_timeout_returns_minus_one(tmp_path):
    import subprocess
    from core.engine import run_command
    log_file = str(tmp_path / "timeout.log")

    with patch("core.engine.subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="sleep", timeout=1)):
        exit_code = run_command("sleep 100", log_file=log_file, tool_name="test", target="localhost", timeout=1)
    assert exit_code == -1


def test_run_command_file_not_found_returns_minus_two(tmp_path):
    from core.engine import run_command
    log_file = str(tmp_path / "nf.log")

    with patch("core.engine.subprocess.run", side_effect=FileNotFoundError("not found")):
        exit_code = run_command("nonexistent_binary_xyz", log_file=log_file, tool_name="test", target="localhost")
    assert exit_code == -2


def test_run_command_generic_exception_returns_minus_three(tmp_path):
    from core.engine import run_command
    log_file = str(tmp_path / "exc.log")

    with patch("core.engine.subprocess.run", side_effect=RuntimeError("boom")):
        exit_code = run_command("echo test", log_file=log_file, tool_name="test", target="localhost")
    assert exit_code == -3


def test_run_command_creates_log_dir(tmp_path):
    from core.engine import run_command
    nested = tmp_path / "a" / "b" / "c" / "test.log"
    exit_code = run_command("echo deep", log_file=str(nested), tool_name="test", target="localhost")
    assert exit_code == 0
    assert nested.exists()


def test_run_command_writes_cmd_header(tmp_path):
    from core.engine import run_command
    log_file = str(tmp_path / "header.log")
    run_command("echo test", log_file=log_file, tool_name="my_tool", target="t")

    content = Path(log_file).read_text()
    assert "[CMD] my_tool" in content


def test_run_parallel_partial_failure(tmp_path):
    from core.engine import run_parallel
    commands = [
        {"cmd": "echo ok", "log_file": str(tmp_path / "ok.log"), "tool_name": "t", "target": "t"},
        {"cmd": "exit 42", "log_file": str(tmp_path / "fail.log"), "tool_name": "t", "target": "t"},
    ]
    results = run_parallel(commands, max_workers=2)
    assert 0 in results
    assert 42 in results


def test_run_parallel_empty_list(tmp_path):
    from core.engine import run_parallel
    results = run_parallel([], max_workers=2)
    assert results == []


def test_run_parallel_exception_returns_minus_99(tmp_path):
    from core.engine import run_parallel
    with patch("core.engine.run_command", side_effect=RuntimeError("boom")):
        commands = [
            {"cmd": "failing_cmd", "log_file": str(tmp_path / "exc.log"), "tool_name": "t", "target": "t"},
        ]
        results = run_parallel(commands, max_workers=1)
        assert results == [-99]


def test_run_parallel_single_command(tmp_path):
    from core.engine import run_parallel
    commands = [
        {"cmd": "echo single", "log_file": str(tmp_path / "single.log"), "tool_name": "t", "target": "t"},
    ]
    results = run_parallel(commands, max_workers=1)
    assert results == [0]
