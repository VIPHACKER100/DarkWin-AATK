"""
DARKWIN — Integration Tests | Full Scan Pipeline
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_full_scan_pipeline_creates_output(tmp_path):
    with patch("core.config_loader.load_config") as mock_config:
        mock_config.return_value = {
            "output_dir": str(tmp_path / "reports"),
            "log_dir": str(tmp_path / "logs"),
            "default_threads": 5,
            "tools": {},
            "wordlists": {},
            "api_keys": {"github_token": "", "hibp_api_key": ""},
            "nuclei_templates": "nuclei-templates",
        }
        with patch("core.config_loader.get_output_dir") as mock_outdir:
            out_dir = tmp_path / "reports" / "example.com" / "full_scan_session"
            out_dir.mkdir(parents=True)
            (out_dir / "whois.txt").write_text("Domain: example.com")
            mock_outdir.return_value = str(out_dir)

            with patch("core.engine.run_command", return_value=0), \
                 patch("requests.get", return_value=MagicMock(status_code=404, text="", json=lambda: [])), \
                 patch("requests.head", return_value=MagicMock(status_code=404)), \
                 patch("core.logger.setup_logger"), \
                 patch("core.logger.get_logger", return_value=MagicMock()), \
                 patch("automation.recon_pipeline.run", return_value=str(out_dir / "report.html")):

                from automation.full_scan_pipeline import run
                report_path = run("example.com")

    assert Path(report_path).exists()


def test_full_scan_pipeline_generates_html(tmp_path):
    with patch("core.config_loader.load_config") as mock_config:
        mock_config.return_value = {
            "output_dir": str(tmp_path / "reports"),
            "log_dir": str(tmp_path / "logs"),
            "default_threads": 5,
            "tools": {},
            "wordlists": {},
            "api_keys": {"github_token": "", "hibp_api_key": ""},
            "nuclei_templates": "nuclei-templates",
        }
        with patch("core.config_loader.get_output_dir") as mock_outdir:
            out_dir = tmp_path / "reports" / "target.com" / "session"
            out_dir.mkdir(parents=True)
            (out_dir / "nmap.txt").write_text("PORT 80 open\nPORT 443 open\n")
            mock_outdir.return_value = str(out_dir)

            with patch("core.engine.run_command", return_value=0), \
                 patch("requests.get", return_value=MagicMock(status_code=404, text="", json=lambda: [])), \
                 patch("requests.head", return_value=MagicMock(status_code=404)), \
                 patch("core.logger.setup_logger"), \
                 patch("core.logger.get_logger", return_value=MagicMock()), \
                 patch("automation.recon_pipeline.run", return_value=str(out_dir / "report.html")):

                from automation.full_scan_pipeline import run
                report_path = run("target.com")

    content = Path(report_path).read_text(encoding="utf-8")
    assert "DARKWIN" in content
