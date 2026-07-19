"""
DARKWIN — Unit Tests | Tool Loader
"""

import pytest
from unittest.mock import patch


def test_check_tool_returns_true_for_existing_binary():
    from core.tool_loader import check_tool
    assert check_tool("python3") is True


def test_check_tool_returns_false_for_nonexistent_binary():
    from core.tool_loader import check_tool
    assert check_tool("nonexistent_tool_xyz_12345") is False


def test_check_tool_returns_true_for_ls():
    from core.tool_loader import check_tool
    assert check_tool("ls") is True


@patch("core.tool_loader.check_tool", return_value=True)
def test_verify_all_tools_all_found(mock_check):
    from core.tool_loader import verify_all_tools
    config = {"tools": {"nmap": "nmap", "subfinder": "subfinder"}}
    results = verify_all_tools(config)
    assert results == {"nmap": True, "subfinder": True}


@patch("core.tool_loader.check_tool", side_effect=[True, False, True])
def test_verify_all_tools_mixed(mock_check):
    from core.tool_loader import verify_all_tools
    config = {"tools": {"nmap": "nmap", "amass": "amass", "ls": "ls"}}
    results = verify_all_tools(config)
    assert results["nmap"] is True
    assert results["amass"] is False
    assert results["ls"] is True


def test_verify_all_tools_empty_config():
    from core.tool_loader import verify_all_tools
    results = verify_all_tools({})
    assert results == {}


def test_verify_all_tools_empty_tools():
    from core.tool_loader import verify_all_tools
    results = verify_all_tools({"tools": {}})
    assert results == {}


@patch("core.tool_loader.check_tool", return_value=False)
def test_verify_all_tools_returns_all_names_as_keys(mock_check):
    from core.tool_loader import verify_all_tools
    config = {"tools": {"a": "a", "b": "b", "c": "c"}}
    results = verify_all_tools(config)
    assert set(results.keys()) == {"a", "b", "c"}
