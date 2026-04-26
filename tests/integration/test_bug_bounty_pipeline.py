"""
DARKWIN — Integration Tests | Bug Bounty Pipeline
Tests the bug bounty pipeline with all external tool calls mocked.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


def test_bug_bounty_pipeline_creates_output_files(tmp_path):
    """Bug bounty pipeline should produce expected output files."""
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
            out_dir = tmp_path / "reports" / "example.com" / "bounty_session"
            out_dir.mkdir(parents=True)
            (out_dir / "subdomains_all.txt").write_text("sub.example.com\n")
            (out_dir / "all_urls.txt").write_text("https://example.com/page?id=1\n")
            mock_outdir.return_value = str(out_dir)

            with patch("core.engine.run_command", return_value=0), \
                 patch("requests.get", return_value=MagicMock(status_code=404, text="", json=lambda: [])), \
                 patch("requests.head", return_value=MagicMock(status_code=404)), \
                 patch("core.logger.setup_logger"), \
                 patch("core.logger.get_logger", return_value=MagicMock()), \
                 patch("automation.recon_pipeline.run", return_value=str(out_dir / "report.html")):

                from automation.bug_bounty_pipeline import run
                report_path = run("example.com")

    assert Path(report_path).exists()
