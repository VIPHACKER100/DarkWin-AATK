"""
DARKWIN — Unit Tests | Fuzzing Module run() Functions
"""

import pytest
from pathlib import Path
from unittest.mock import patch


@patch("modules.fuzzing.directory_fuzzer.run_tool")
@patch("modules.fuzzing.directory_fuzzer.load_config")
def test_directory_fuzzer_run(mock_config, mock_run_tool, tmp_path):
    from modules.fuzzing.directory_fuzzer import run
    mock_config.return_value = {"wordlists": {"directories": "common.txt"}}

    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "ffuf" in cmd
    assert "FUZZ" in cmd


@patch("modules.fuzzing.directory_fuzzer.run_tool")
def test_directory_fuzzer_adds_https(mock_run_tool, tmp_path):
    from modules.fuzzing.directory_fuzzer import run
    run("example.com", str(tmp_path), wordlist="list.txt")

    cmd = mock_run_tool.call_args[0][0]
    assert "https://example.com" in cmd


@patch("modules.fuzzing.directory_fuzzer.run_tool")
def test_directory_fuzzer_preserves_http(mock_run_tool, tmp_path):
    from modules.fuzzing.directory_fuzzer import run
    run("http://example.com", str(tmp_path), wordlist="list.txt")

    cmd = mock_run_tool.call_args[0][0]
    assert "http://example.com" in cmd
    assert cmd.count("https://") <= 1


@patch("modules.fuzzing.directory_fuzzer.run_tool")
def test_directory_fuzzer_strips_trailing_slash(mock_run_tool, tmp_path):
    from modules.fuzzing.directory_fuzzer import run
    run("example.com/", str(tmp_path), wordlist="list.txt")

    cmd = mock_run_tool.call_args[0][0]
    assert "example.com/" not in cmd or "example.com/FUZZ" in cmd


@patch("modules.fuzzing.api_fuzzer.run_tool")
@patch("modules.fuzzing.api_fuzzer.load_config")
def test_api_fuzzer_run(mock_config, mock_run_tool, tmp_path):
    from modules.fuzzing.api_fuzzer import run
    mock_config.return_value = {"wordlists": {"directories": "common.txt"}}

    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "ffuf" in cmd
    assert "api/FUZZ" in cmd


@patch("modules.fuzzing.api_fuzzer.run_tool")
def test_api_fuzzer_adds_https(mock_run_tool, tmp_path):
    from modules.fuzzing.api_fuzzer import run
    run("example.com", str(tmp_path), wordlist="list.txt")

    cmd = mock_run_tool.call_args[0][0]
    assert "https://example.com" in cmd


@patch("modules.fuzzing.parameter_fuzzer.run_tool")
@patch("modules.fuzzing.parameter_fuzzer.load_config")
def test_parameter_fuzzer_run(mock_config, mock_run_tool, tmp_path):
    from modules.fuzzing.parameter_fuzzer import run
    mock_config.return_value = {"wordlists": {"parameters": "params.txt"}}

    run("https://example.com/page", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "wfuzz" in cmd
    assert "FUZZ" in cmd


@patch("modules.fuzzing.parameter_fuzzer.run_tool")
def test_parameter_fuzzer_adds_fuzz_param(mock_run_tool, tmp_path):
    from modules.fuzzing.parameter_fuzzer import run
    run("https://example.com/page", str(tmp_path), wordlist="params.txt")

    cmd = mock_run_tool.call_args[0][0]
    assert "FUZZ" in cmd
