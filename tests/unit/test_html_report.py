"""
DARKWIN — Unit Tests | HTML Report Generator
"""

import pytest
from pathlib import Path
from unittest.mock import patch


def test_html_report_generate_creates_file(tmp_path):
    from modules.reporting.html_report import generate
    results = {
        "target": "example.com",
        "output_dir": str(tmp_path),
        "modules": {
            "whois": {"file": "whois.txt", "type": "txt", "content": "Domain: example.com"},
            "subdomains": {"file": "subs.txt", "type": "txt", "content": "sub.example.com"},
        },
    }

    report_path = generate(results, str(tmp_path))
    assert Path(report_path).exists()
    assert report_path.endswith("report.html")


def test_html_report_contains_target(tmp_path):
    from modules.reporting.html_report import generate
    results = {
        "target": "example.com",
        "output_dir": str(tmp_path),
        "modules": {},
    }

    report_path = generate(results, str(tmp_path))
    content = Path(report_path).read_text(encoding="utf-8")
    assert "example.com" in content


def test_html_report_contains_darkwin(tmp_path):
    from modules.reporting.html_report import generate
    results = {
        "target": "test.com",
        "output_dir": str(tmp_path),
        "modules": {},
    }

    report_path = generate(results, str(tmp_path))
    content = Path(report_path).read_text(encoding="utf-8")
    assert "DARKWIN" in content


def test_html_report_contains_module_data(tmp_path):
    from modules.reporting.html_report import generate
    results = {
        "target": "example.com",
        "output_dir": str(tmp_path),
        "modules": {
            "nuclei": {"file": "nuclei.txt", "type": "txt", "content": "CRITICAL: CVE-2021-1234"},
            "nmap": {"file": "nmap.txt", "type": "txt", "content": "PORT 80 open"},
        },
    }

    report_path = generate(results, str(tmp_path))
    content = Path(report_path).read_text(encoding="utf-8")
    assert "nuclei" in content.lower() or "Nuclei" in content
    assert "nmap" in content.lower() or "Nmap" in content


def test_html_report_empty_modules(tmp_path):
    from modules.reporting.html_report import generate
    results = {
        "target": "empty.com",
        "output_dir": str(tmp_path),
        "modules": {},
    }

    report_path = generate(results, str(tmp_path))
    assert Path(report_path).exists()
    content = Path(report_path).read_text(encoding="utf-8")
    assert "empty.com" in content


def test_html_report_creates_output_dir_if_missing(tmp_path):
    from modules.reporting.html_report import generate
    results = {
        "target": "example.com",
        "output_dir": str(tmp_path),
        "modules": {},
    }

    nested = tmp_path / "deep" / "nested"
    report_path = generate(results, str(nested))
    assert Path(report_path).exists()
