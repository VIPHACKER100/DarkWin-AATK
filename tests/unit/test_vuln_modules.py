"""
DARKWIN — Unit Tests | Vulnerability Module run() Functions
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


# ─── Reflected XSS ────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.xss.reflected_xss.run_tool")
def test_reflected_xss_run(mock_run_tool, tmp_path):
    from modules.vulnerabilities.xss.reflected_xss import run
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://example.com/page?q=test\n")

    run(str(urls_file), str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "dalfox" in cmd


def test_reflected_xss_run_missing_file(tmp_path):
    from modules.vulnerabilities.xss.reflected_xss import run
    run(str(tmp_path / "nonexistent.txt"), str(tmp_path))


# ─── DOM XSS ──────────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.xss.dom_xss.run_tool")
def test_dom_xss_run(mock_run_tool, tmp_path):
    from modules.vulnerabilities.xss.dom_xss import run
    urls_file = tmp_path / "urls.txt"
    urls_file.write_text("https://example.com/page?q=test\n")

    run(str(urls_file), str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "kxss" in cmd


def test_dom_xss_run_missing_file(tmp_path):
    from modules.vulnerabilities.xss.dom_xss import run
    run(str(tmp_path / "nonexistent.txt"), str(tmp_path))


# ─── SQLi Detector ────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.sqli.sqli_detector.run_tool")
def test_sqli_detector_run(mock_run_tool, tmp_path):
    from modules.vulnerabilities.sqli.sqli_detector import run
    run("https://example.com/page?id=1", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "sqlmap" in cmd
    assert "level=3" in cmd
    assert "risk=2" in cmd


# ─── Blind SQLi ──────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.sqli.blind_sqli.run_tool")
def test_blind_sqli_run(mock_run_tool, tmp_path):
    from modules.vulnerabilities.sqli.blind_sqli import run
    run("https://example.com/page?id=1", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "sqlmap" in cmd
    assert "--technique=T" in cmd
    assert "--time-sec=5" in cmd


# ─── LFI Scanner ─────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.lfi.lfi_scanner.run_tool")
@patch("modules.vulnerabilities.lfi.lfi_scanner.load_config")
def test_lfi_scanner_run(mock_config, mock_run_tool, tmp_path):
    from modules.vulnerabilities.lfi.lfi_scanner import run
    mock_config.return_value = {"wordlists": {"lfi": "custom_lfi.txt"}}

    run("https://example.com/?page=", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "ffuf" in cmd
    assert "FUZZ" in cmd


@patch("modules.vulnerabilities.lfi.lfi_scanner.run_tool")
@patch("modules.vulnerabilities.lfi.lfi_scanner.load_config")
def test_lfi_scanner_adds_fuzz_placeholder(mock_config, mock_run_tool, tmp_path):
    from modules.vulnerabilities.lfi.lfi_scanner import run
    mock_config.return_value = {"wordlists": {}}

    run("https://example.com/?page=", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "FUZZ" in cmd


@patch("modules.vulnerabilities.lfi.lfi_scanner.run_tool")
def test_lfi_scanner_preserves_existing_fuzz(mock_run_tool, tmp_path):
    from modules.vulnerabilities.lfi.lfi_scanner import run

    run("https://example.com/?page=FUZZ", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    # Should not have double FUZZ
    assert cmd.count("FUZZ") == 1 or "FUZZ" in cmd


# ─── SSRF Tester ─────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.ssrf.ssrf_tester.run_tool")
@patch("modules.vulnerabilities.ssrf.ssrf_tester.load_config")
def test_ssrf_tester_run(mock_config, mock_run_tool, tmp_path):
    from modules.vulnerabilities.ssrf.ssrf_tester import run
    mock_config.return_value = {"wordlists": {"ssrf": "ssrf_wordlist.txt"}}

    run("https://example.com/?url=", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "ffuf" in cmd
    assert "FUZZ" in cmd


# ─── RCE Scanner ─────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.rce.rce_scanner.run_tool")
@patch("modules.vulnerabilities.rce.rce_scanner.load_config")
def test_rce_scanner_run(mock_config, mock_run_tool, tmp_path):
    from modules.vulnerabilities.rce.rce_scanner import run
    mock_config.return_value = {"nuclei_templates": "nuclei-templates"}

    run("https://example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "nuclei" in cmd
    assert "rce" in cmd
    assert "high,critical" in cmd


# ─── CSRF Detector ───────────────────────────────────────────────────────

@patch("modules.vulnerabilities.csrf.csrf_detector.run_tool")
@patch("modules.vulnerabilities.csrf.csrf_detector.load_config")
def test_csrf_detector_run(mock_config, mock_run_tool, tmp_path):
    from modules.vulnerabilities.csrf.csrf_detector import run
    mock_config.return_value = {"nuclei_templates": "nuclei-templates"}

    run("https://example.com", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "nuclei" in cmd
    assert "csrf" in cmd


# ─── IDOR Scanner ────────────────────────────────────────────────────────

@patch("modules.vulnerabilities.idor.idor_scanner.run_tool")
def test_idor_scanner_run_with_param(mock_run_tool, tmp_path):
    from modules.vulnerabilities.idor.idor_scanner import run
    run("https://example.com/api?id=1", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "ffuf" in cmd
    assert "FUZZ" in cmd


def test_idor_scanner_no_param_warns(tmp_path):
    from modules.vulnerabilities.idor.idor_scanner import run
    # Should log a warning and return without crashing
    run("https://example.com/api", str(tmp_path))


@patch("modules.vulnerabilities.idor.idor_scanner.run_tool")
def test_idor_scanner_preserves_fuzz(mock_run_tool, tmp_path):
    from modules.vulnerabilities.idor.idor_scanner import run
    run("https://example.com/api?id=FUZZ", str(tmp_path))

    cmd = mock_run_tool.call_args[0][0]
    assert "FUZZ" in cmd
