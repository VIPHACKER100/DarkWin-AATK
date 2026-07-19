"""
DARKWIN — Unit Tests | Recon Helper Functions
"""

import pytest
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock


# ─── Subdomain Enum Helpers ───────────────────────────────────────────────

def test_merge_subdomain_files_deduplicates(tmp_path):
    from modules.recon.subdomain_enum import _merge_subdomain_files

    f1 = tmp_path / "file1.txt"
    f2 = tmp_path / "file2.txt"
    output = tmp_path / "merged.txt"

    f1.write_text("a.example.com\nb.example.com\na.example.com\n")
    f2.write_text("b.example.com\nc.example.com\n")

    _merge_subdomain_files([str(f1), str(f2)], str(output))

    lines = output.read_text().strip().split("\n")
    assert len(lines) == 3
    assert set(lines) == {"a.example.com", "b.example.com", "c.example.com"}


def test_merge_subdomain_files_empty_input(tmp_path):
    from modules.recon.subdomain_enum import _merge_subdomain_files

    f1 = tmp_path / "empty.txt"
    output = tmp_path / "merged.txt"
    f1.write_text("")

    _merge_subdomain_files([str(f1)], str(output))
    content = output.read_text().strip()
    assert content == ""


def test_merge_subdomain_files_nonexistent_file(tmp_path):
    from modules.recon.subdomain_enum import _merge_subdomain_files

    output = tmp_path / "merged.txt"
    _merge_subdomain_files([str(tmp_path / "does_not_exist.txt")], str(output))
    assert output.exists()
    assert output.read_text().strip() == ""


def test_merge_subdomain_files_blank_lines_ignored(tmp_path):
    from modules.recon.subdomain_enum import _merge_subdomain_files

    f1 = tmp_path / "file1.txt"
    output = tmp_path / "merged.txt"
    f1.write_text("\n\na.example.com\n\n\nb.example.com\n\n")

    _merge_subdomain_files([str(f1)], str(output))
    lines = output.read_text().strip().split("\n")
    assert len(lines) == 2


# ─── S3 Bucket Helpers ────────────────────────────────────────────────────

def test_generate_bucket_names_returns_list():
    from modules.recon.s3_bucket_scan import _generate_bucket_names
    names = _generate_bucket_names("example-com")
    assert isinstance(names, list)
    assert len(names) > 0


def test_generate_bucket_names_contains_base():
    from modules.recon.s3_bucket_scan import _generate_bucket_names
    names = _generate_bucket_names("example-com")
    assert "example-com" in names


def test_generate_bucket_names_has_prefixes():
    from modules.recon.s3_bucket_scan import _generate_bucket_names
    names = _generate_bucket_names("example-com")
    assert "dev-example-com" in names
    assert "prod-example-com" in names
    assert "backup-example-com" in names


def test_generate_bucket_names_has_suffixes():
    from modules.recon.s3_bucket_scan import _generate_bucket_names
    names = _generate_bucket_names("example-com")
    assert "example-com-dev" in names
    assert "example-com-staging" in names
    assert "example-com-prod" in names


def test_generate_bucket_names_no_duplicates():
    from modules.recon.s3_bucket_scan import _generate_bucket_names
    names = _generate_bucket_names("test")
    assert len(names) == len(set(names))


def test_generate_bucket_names_expected_count():
    from modules.recon.s3_bucket_scan import _generate_bucket_names, PERMUTATION_PREFIXES, PERMUTATION_SUFFIXES
    names = _generate_bucket_names("test")
    expected_max = len(PERMUTATION_PREFIXES) * len(PERMUTATION_SUFFIXES)
    assert len(names) <= expected_max


@patch("modules.recon.s3_bucket_scan.requests.head")
def test_check_bucket_returns_status_code(mock_head):
    from modules.recon.s3_bucket_scan import _check_bucket
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_head.return_value = mock_resp

    status = _check_bucket("https://bucket.s3.amazonaws.com")
    assert status == 200


@patch("modules.recon.s3_bucket_scan.requests.head")
def test_check_bucket_returns_403(mock_head):
    from modules.recon.s3_bucket_scan import _check_bucket
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_head.return_value = mock_resp

    status = _check_bucket("https://bucket.s3.amazonaws.com")
    assert status == 403


@patch("modules.recon.s3_bucket_scan.requests.head", side_effect=requests.RequestException("connection error"))
def test_check_bucket_returns_zero_on_error(mock_head):
    from modules.recon.s3_bucket_scan import _check_bucket
    status = _check_bucket("https://bucket.s3.amazonaws.com")
    assert status == 0


# ─── GitHub Dorking Helpers ──────────────────────────────────────────────

def test_dork_patterns_has_entries():
    from modules.recon.github_dorking import DORK_PATTERNS
    assert len(DORK_PATTERNS) > 0


def test_dork_patterns_contain_target_placeholder():
    from modules.recon.github_dorking import DORK_PATTERNS
    for pattern in DORK_PATTERNS:
        assert "{target}" in pattern


@patch("modules.recon.github_dorking.requests.get")
def test_search_github_api_returns_items(mock_get):
    from modules.recon.github_dorking import _search_github_api
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"items": [{"name": "test.py", "html_url": "https://github.com/test"}]}
    mock_get.return_value = mock_resp

    mock_log = MagicMock()
    items = _search_github_api("test query", "fake_token", mock_log)
    assert len(items) == 1
    assert items[0]["name"] == "test.py"


@patch("modules.recon.github_dorking.requests.get")
def test_search_github_api_returns_empty_on_403(mock_get):
    from modules.recon.github_dorking import _search_github_api
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_get.return_value = mock_resp

    mock_log = MagicMock()
    items = _search_github_api("test", "token", mock_log)
    assert items == []
    mock_log.warning.assert_called()


@patch("modules.recon.github_dorking.requests.get")
def test_search_github_api_returns_empty_on_error(mock_get):
    from modules.recon.github_dorking import _search_github_api
    mock_get.side_effect = requests.RequestException("network error")

    mock_log = MagicMock()
    items = _search_github_api("test", "token", mock_log)
    assert items == []
    mock_log.error.assert_called()


@patch("modules.recon.github_dorking.requests.get")
def test_search_github_api_returns_empty_on_404(mock_get):
    from modules.recon.github_dorking import _search_github_api
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    mock_log = MagicMock()
    items = _search_github_api("test", "token", mock_log)
    assert items == []
