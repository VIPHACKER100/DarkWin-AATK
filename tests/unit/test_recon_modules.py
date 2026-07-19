"""
DARKWIN — Unit Tests | Recon Module run() Functions
All external tool calls are mocked.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ─── Subdomain Enum ───────────────────────────────────────────────────────

@patch("modules.recon.subdomain_enum.engine.run_command")
@patch("modules.recon.subdomain_enum._merge_subdomain_files")
def test_subdomain_enum_run_calls_tools(mock_merge, mock_cmd, tmp_path):
    from modules.recon.subdomain_enum import run
    mock_cmd.return_value = 0

    run("example.com", str(tmp_path))

    assert mock_cmd.call_count == 2
    calls = [c[0][0] for c in mock_cmd.call_args_list]
    assert any("subfinder" in c for c in calls)
    assert any("amass" in c for c in calls)
    mock_merge.assert_called_once()


# ─── DNS Bruteforce ───────────────────────────────────────────────────────

@patch("modules.recon.dns_bruteforce.run_tool")
@patch("modules.recon.dns_bruteforce.load_config")
def test_dns_bruteforce_uses_default_wordlist(mock_config, mock_run_tool, tmp_path):
    from modules.recon.dns_bruteforce import run
    mock_config.return_value = {"wordlists": {"dns": "custom_wordlist.txt"}}

    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "dnsrecon" in cmd
    assert "example.com" in cmd


@patch("modules.recon.dns_bruteforce.run_tool")
def test_dns_bruteforce_custom_wordlist(mock_run_tool, tmp_path):
    from modules.recon.dns_bruteforce import run
    run("example.com", str(tmp_path), wordlist="/custom/list.txt")

    cmd = mock_run_tool.call_args[0][0]
    assert "/custom/list.txt" in cmd


# ─── WHOIS Lookup ─────────────────────────────────────────────────────────

@patch("modules.recon.whois_lookup.run_tool")
def test_whois_lookup_run(mock_run_tool, tmp_path):
    from modules.recon.whois_lookup import run
    run("example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "whois" in cmd
    assert "example.com" in cmd


# ─── ASN Lookup ───────────────────────────────────────────────────────────

@patch("modules.recon.asn_lookup.run_tool")
def test_asn_lookup_run_calls_two_tools(mock_run_tool, tmp_path):
    from modules.recon.asn_lookup import run
    run("example.com", str(tmp_path))

    assert mock_run_tool.call_count == 2
    calls = [c[0][0] for c in mock_run_tool.call_args_list]
    assert any("whois" in c for c in calls)
    assert any("bgp.he.net" in c for c in calls)


# ─── Reverse IP ───────────────────────────────────────────────────────────

@patch("modules.recon.reverse_ip.engine.run_command")
@patch("modules.recon.reverse_ip.requests.get")
def test_reverse_ip_run_uses_hackertarget(mock_get, mock_cmd, tmp_path):
    from modules.recon.reverse_ip import run
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "other.com\n"
    mock_get.return_value = mock_resp
    mock_cmd.return_value = 0

    run("1.2.3.4", str(tmp_path))

    mock_get.assert_called_once()
    assert "hackertarget.com" in mock_get.call_args[0][0]
    mock_cmd.assert_called_once()
    assert "hakrevdns" in mock_cmd.call_args[0][0]


@patch("modules.recon.reverse_ip.engine.run_command")
@patch("modules.recon.reverse_ip.requests.get")
def test_reverse_ip_run_handles_api_error(mock_get, mock_cmd, tmp_path):
    from modules.recon.reverse_ip import run
    import requests
    mock_get.side_effect = requests.RequestException("timeout")
    mock_cmd.return_value = 0

    run("1.2.3.4", str(tmp_path))
    mock_cmd.assert_called_once()


# ─── S3 Bucket Scan ──────────────────────────────────────────────────────

@patch("modules.recon.s3_bucket_scan._check_bucket", return_value=404)
def test_s3_bucket_scan_run_creates_output_file(mock_check, tmp_path):
    from modules.recon.s3_bucket_scan import run
    run("example.com", str(tmp_path))

    out_file = tmp_path / "s3_buckets.txt"
    assert out_file.exists()
    content = out_file.read_text()
    assert "S3 Bucket Scan" in content


@patch("modules.recon.s3_bucket_scan._check_bucket", return_value=200)
def test_s3_bucket_scan_finds_open_bucket(mock_check, tmp_path):
    from modules.recon.s3_bucket_scan import run
    run("example.com", str(tmp_path))

    out_file = tmp_path / "s3_buckets.txt"
    content = out_file.read_text()
    assert "OPEN (200)" in content


@patch("modules.recon.s3_bucket_scan._check_bucket", return_value=403)
def test_s3_bucket_scan_finds_forbidden_bucket(mock_check, tmp_path):
    from modules.recon.s3_bucket_scan import run
    run("example.com", str(tmp_path))

    out_file = tmp_path / "s3_buckets.txt"
    content = out_file.read_text()
    assert "FORBIDDEN (403" in content


# ─── GitHub Dorking ──────────────────────────────────────────────────────

@patch("modules.recon.github_dorking.load_config")
def test_github_dorking_no_token_saves_urls_only(mock_config, tmp_path):
    from modules.recon.github_dorking import run
    mock_config.return_value = {"api_keys": {"github_token": ""}}

    run("example.com", str(tmp_path))

    out_file = tmp_path / "github_dorks.txt"
    assert out_file.exists()
    content = out_file.read_text()
    assert "github.com/search" in content
    assert "example.com" in content


@patch("modules.recon.github_dorking._search_github_api", return_value=[{"name": "test.py", "html_url": "https://github.com/test", "repository": {"full_name": "org/repo"}}])
@patch("modules.recon.github_dorking.load_config")
def test_github_dorking_with_token_calls_api(mock_config, mock_api, tmp_path):
    from modules.recon.github_dorking import run
    mock_config.return_value = {"api_keys": {"github_token": "ghp_test123"}}

    run("example.com", str(tmp_path))

    assert mock_api.call_count > 0
    out_file = tmp_path / "github_dorks.txt"
    content = out_file.read_text()
    assert "API Results" in content
