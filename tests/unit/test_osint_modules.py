"""
DARKWIN — Unit Tests | OSINT Module run() Functions
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@patch("modules.osint.email_harvester.run_tool")
def test_email_harvester_run(mock_run_tool, tmp_path):
    from modules.osint.email_harvester import run
    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "theHarvester" in cmd
    assert "example.com" in cmd


@patch("modules.osint.social_media_enum.run_tool")
def test_social_media_enum_run(mock_run_tool, tmp_path):
    from modules.osint.social_media_enum import run
    run("testuser", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "sherlock" in cmd
    assert "testuser" in cmd


@patch("modules.osint.metadata_scraper.run_tool")
def test_metadata_scraper_run(mock_run_tool, tmp_path):
    from modules.osint.metadata_scraper import run
    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "metagoofil" in cmd
    assert "example.com" in cmd


@patch("modules.osint.breach_lookup.load_config")
@patch("modules.osint.breach_lookup._query_hibp")
def test_breach_lookup_run_with_key(mock_hibp, mock_config, tmp_path):
    from modules.osint.breach_lookup import run
    mock_config.return_value = {"api_keys": {"hibp_api_key": "test_key"}}
    mock_hibp.return_value = []

    run("test@example.com", str(tmp_path))

    out_file = tmp_path / "breach.json"
    assert out_file.exists()
    import json
    data = json.loads(out_file.read_text())
    assert data["email"] == "test@example.com"
    assert data["breach_count"] == 0


@patch("modules.osint.breach_lookup.load_config")
def test_breach_lookup_run_no_key_skips(mock_config, tmp_path):
    from modules.osint.breach_lookup import run
    mock_config.return_value = {"api_keys": {"hibp_api_key": ""}}

    run("test@example.com", str(tmp_path))

    out_file = tmp_path / "breach.json"
    assert not out_file.exists()
