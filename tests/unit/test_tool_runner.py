"""
DARKWIN — Unit Tests | Tool Runner
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@patch("core.tool_runner.engine.run_command")
@patch("core.tool_runner.get_logger")
def test_run_tool_creates_output_dir(mock_logger, mock_run_cmd, tmp_path):
    from core.tool_runner import run_tool
    mock_logger.return_value = MagicMock()
    mock_run_cmd.return_value = 0

    output_dir = str(tmp_path / "new_output")
    run_tool("echo test", output_dir, "test_tool", "target.com")

    assert Path(output_dir).exists()


@patch("core.tool_runner.engine.run_command")
@patch("core.tool_runner.get_logger")
def test_run_tool_calls_run_command(mock_logger, mock_run_cmd, tmp_path):
    from core.tool_runner import run_tool
    mock_logger.return_value = MagicMock()
    mock_run_cmd.return_value = 0

    output_dir = str(tmp_path / "out")
    run_tool("nmap -sV target", output_dir, "port_scanner", "192.168.1.1")

    mock_run_cmd.assert_called_once()
    call_args = mock_run_cmd.call_args
    assert call_args[0][0] == "nmap -sV target"
    assert call_args[1]["tool_name"] == "port_scanner"


@patch("core.tool_runner.engine.run_command")
@patch("core.tool_runner.get_logger")
def test_run_tool_passes_correct_log_file(mock_logger, mock_run_cmd, tmp_path):
    from core.tool_runner import run_tool
    mock_logger.return_value = MagicMock()
    mock_run_cmd.return_value = 0

    output_dir = str(tmp_path / "scan")
    run_tool("test_cmd", output_dir, "my_tool", "target")

    call_args = mock_run_cmd.call_args
    expected_log = f"{output_dir}/my_tool.log"
    assert call_args[1]["log_file"] == expected_log


@patch("core.tool_runner.engine.run_command")
@patch("core.tool_runner.get_logger")
def test_run_tool_returns_none(mock_logger, mock_run_cmd, tmp_path):
    from core.tool_runner import run_tool
    mock_logger.return_value = MagicMock()
    mock_run_cmd.return_value = 0

    result = run_tool("echo hi", str(tmp_path / "x"), "tool", "t")
    assert result is None
