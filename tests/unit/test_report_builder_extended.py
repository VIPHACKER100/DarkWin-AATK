"""
DARKWIN — Unit Tests | Report Builder (Extended)
"""

import pytest
import json
from pathlib import Path


def test_collect_results_nonexistent_dir(tmp_path):
    from modules.reporting.report_builder import collect_results
    results = collect_results(str(tmp_path / "does_not_exist"))
    assert results["modules"] == {}


def test_collect_results_skips_log_files(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "test.com" / "session1"
    out_dir.mkdir(parents=True)

    (out_dir / "test.log").write_text("log content")
    (out_dir / "result.txt").write_text("result content")

    results = collect_results(str(out_dir))
    assert "test" not in results["modules"]
    assert "result" in results["modules"]


def test_collect_results_reads_xml(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "test.com" / "session1"
    out_dir.mkdir(parents=True)

    (out_dir / "nmap.xml").write_text("<nmaprun>data</nmaprun>")

    results = collect_results(str(out_dir))
    assert "nmap" in results["modules"]
    assert results["modules"]["nmap"]["type"] == "txt"


def test_collect_results_reads_csv(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "test.com" / "session1"
    out_dir.mkdir(parents=True)

    (out_dir / "dns_brute.csv").write_text("host,ip\na.com,1.2.3.4\n")

    results = collect_results(str(out_dir))
    assert "dns_brute" in results["modules"]


def test_collect_results_malformed_json_falls_back_to_txt(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "test.com" / "session1"
    out_dir.mkdir(parents=True)

    (out_dir / "broken.json").write_text("this is not json {{{")

    results = collect_results(str(out_dir))
    assert "broken" in results["modules"]
    assert results["modules"]["broken"]["type"] == "txt"


def test_collect_results_disambiguates_duplicate_keys(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "test.com" / "session1"
    sub = out_dir / "subdir"
    sub.mkdir(parents=True)

    (out_dir / "result.txt").write_text("top level")
    (sub / "result.txt").write_text("nested")

    results = collect_results(str(out_dir))
    assert len(results["modules"]) == 2


def test_collect_results_empty_dir(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "test.com" / "session1"
    out_dir.mkdir(parents=True)

    results = collect_results(str(out_dir))
    assert results["modules"] == {}
    assert results["target"] == "test.com"


def test_collect_results_target_from_path(tmp_path):
    from modules.reporting.report_builder import collect_results
    out_dir = tmp_path / "reports" / "myapp.internal.co" / "2025-01-01"
    out_dir.mkdir(parents=True)
    (out_dir / "test.txt").write_text("data")

    results = collect_results(str(out_dir))
    assert results["target"] == "myapp.internal.co"
