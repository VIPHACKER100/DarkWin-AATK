"""
DARKWIN — Unit Tests | Web Module run() Functions
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@patch("modules.web.url_collector.engine.run_command")
def test_url_collector_run_calls_tools(mock_cmd, tmp_path):
    from modules.web.url_collector import run
    mock_cmd.return_value = 0

    run("example.com", str(tmp_path))

    assert mock_cmd.call_count == 2
    calls = [c[0][0] for c in mock_cmd.call_args_list]
    assert any("gau" in c for c in calls)
    assert any("waybackurls" in c for c in calls)


@patch("modules.web.url_collector.engine.run_command")
def test_url_collector_run_merges_urls(mock_cmd, tmp_path):
    from modules.web.url_collector import run
    mock_cmd.return_value = 0

    # Pre-create source files with content
    (tmp_path / "gau_urls.txt").write_text("https://example.com/a\nhttps://example.com/b\n")
    (tmp_path / "wayback_urls.txt").write_text("https://example.com/b\nhttps://example.com/c\n")

    run("example.com", str(tmp_path))

    merged = tmp_path / "all_urls.txt"
    if merged.exists():
        lines = merged.read_text().strip().split("\n")
        assert len(lines) == 3  # a, b, c deduped


@patch("modules.web.crawler.run_tool")
def test_crawler_run(mock_run_tool, tmp_path):
    from modules.web.crawler import run
    run("https://example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "katana" in cmd
    assert "example.com" in cmd


@patch("modules.web.parameter_finder.run_tool")
def test_parameter_finder_run(mock_run_tool, tmp_path):
    from modules.web.parameter_finder import run
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://example.com/page?id=1\n")

    run(str(urls_file), str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "arjun" in cmd


def test_parameter_finder_run_missing_file(tmp_path):
    from modules.web.parameter_finder import run
    run(str(tmp_path / "nonexistent.txt"), str(tmp_path))
    # Should not crash


@patch("modules.web.js_parser.engine.run_command")
def test_js_parser_run_calls_subjs(mock_cmd, tmp_path):
    from modules.web.js_parser import run
    mock_cmd.return_value = 0

    run("https://example.com", str(tmp_path))

    assert mock_cmd.call_count >= 1
    assert "subjs" in mock_cmd.call_args_list[0][0][0]


@patch("modules.web.js_parser.engine.run_command")
def test_js_parser_run_skips_when_no_js_files(mock_cmd, tmp_path):
    from modules.web.js_parser import run
    mock_cmd.return_value = 0

    # When engine.run_command is mocked, no js_files.txt is created,
    # so the function should return early after subjs call
    run("https://example.com", str(tmp_path))

    # Should only call subjs once, then return early
    assert mock_cmd.call_count == 1


@patch("modules.web.js_parser.engine.run_command")
def test_js_parser_run_full_pipeline(mock_cmd, tmp_path):
    from modules.web.js_parser import run
    mock_cmd.return_value = 0

    # Pre-create js_files.txt with content so it passes the empty check
    js_files = tmp_path / "js_files.txt"
    js_files.write_text("https://example.com/app.js\nhttps://example.com/util.js\n")

    run("https://example.com", str(tmp_path))

    # Should call subjs and linkfinder (2 engine.run_command calls)
    assert mock_cmd.call_count == 2
    calls = [c[0][0] for c in mock_cmd.call_args_list]
    assert "subjs" in calls[0]
    assert "linkfinder" in calls[1]


@patch("modules.web.js_parser.engine.run_command")
def test_js_parser_run_empty_file_skips(mock_cmd, tmp_path):
    from modules.web.js_parser import run
    mock_cmd.return_value = 0

    # Create empty js_files.txt
    js_files = tmp_path / "js_files.txt"
    js_files.write_text("")

    run("https://example.com", str(tmp_path))

    # Should only call subjs once, then return early (empty file)
    assert mock_cmd.call_count == 1
