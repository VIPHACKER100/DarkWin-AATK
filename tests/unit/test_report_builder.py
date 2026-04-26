"""
DARKWIN — Unit Tests | Report Builder
"""

import json
from pathlib import Path


def _setup_mock_output(tmp_path: Path) -> Path:
    """Create a mock scan output directory with sample files."""
    out_dir = tmp_path / "reports" / "example.com" / "2025-01-01_12-00-00"
    out_dir.mkdir(parents=True)

    (out_dir / "subdomains_all.txt").write_text("sub1.example.com\nsub2.example.com\n")
    (out_dir / "whois.txt").write_text("Domain Name: EXAMPLE.COM\nRegistrar: Test Corp\n")
    (out_dir / "nuclei.txt").write_text("[critical] CVE-2021-1234 found at http://sub1.example.com\n")

    api_json = {"results": [{"url": "https://example.com/api/v1", "status": 200}]}
    (out_dir / "api_fuzz.json").write_text(json.dumps(api_json))

    return out_dir


def test_collect_results_returns_dict(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = _setup_mock_output(tmp_path)
    results = collect_results(str(out_dir))
    assert isinstance(results, dict)


def test_collect_results_has_modules_key(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = _setup_mock_output(tmp_path)
    results = collect_results(str(out_dir))
    assert "modules" in results
    assert isinstance(results["modules"], dict)


def test_collect_results_reads_txt_files(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = _setup_mock_output(tmp_path)
    results = collect_results(str(out_dir))
    modules = results["modules"]
    # At least whois and subdomains should be present
    assert len(modules) >= 3


def test_collect_results_reads_json_files(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = _setup_mock_output(tmp_path)
    results = collect_results(str(out_dir))
    # api_fuzz.json should be parsed as JSON
    json_modules = {k: v for k, v in results["modules"].items() if v["type"] == "json"}
    assert len(json_modules) >= 1


def test_collect_results_target_extracted(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = _setup_mock_output(tmp_path)
    results = collect_results(str(out_dir))
    assert results["target"] == "example.com"
