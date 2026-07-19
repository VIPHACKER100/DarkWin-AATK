"""
DARKWIN — Integration Tests | Recon Pipeline (Extended)
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_recon_pipeline_returns_report_path(tmp_path):
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
            out_dir = tmp_path / "reports" / "example.com" / "ext_session"
            out_dir.mkdir(parents=True)
            (out_dir / "whois.txt").write_text("Domain: example.com")
            mock_outdir.return_value = str(out_dir)

            with patch("core.engine.run_command", return_value=0), \
                 patch("requests.get", return_value=MagicMock(status_code=404, text="", json=lambda: [])), \
                 patch("requests.head", return_value=MagicMock(status_code=404)), \
                 patch("core.logger.setup_logger"), \
                 patch("core.logger.get_logger", return_value=MagicMock()):

                from automation.recon_pipeline import run
                report_path = run("example.com")

    assert isinstance(report_path, str)
    assert report_path.endswith("report.html")
    assert Path(report_path).exists()


def test_recon_pipeline_custom_output_dir(tmp_path):
    custom_dir = tmp_path / "custom_output"
    custom_dir.mkdir()

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

        with patch("core.engine.run_command", return_value=0), \
             patch("requests.get", return_value=MagicMock(status_code=404, text="", json=lambda: [])), \
             patch("requests.head", return_value=MagicMock(status_code=404)), \
             patch("core.logger.setup_logger"), \
             patch("core.logger.get_logger", return_value=MagicMock()):

            from automation.recon_pipeline import run
            report_path = run("example.com", output_dir=str(custom_dir))

    assert Path(report_path).exists()
    assert str(custom_dir) in report_path
