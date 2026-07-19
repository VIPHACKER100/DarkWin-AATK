"""
DARKWIN — Integration Tests | Recon Pipeline
Tests the recon pipeline with all external tool calls mocked.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_engine(tmp_path):
    """Patch engine.run_command to do nothing and return 0."""
    with patch("core.engine.run_command", return_value=0) as mock_cmd:
        yield mock_cmd


@pytest.fixture
def mock_requests(tmp_path):
    """Patch requests.get to return an empty response."""
    with patch("requests.get") as mock_get:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_resp.text = ""
        mock_resp.json.return_value = []
        mock_get.return_value = mock_resp
        yield mock_get


@pytest.fixture
def mock_requests_head(tmp_path):
    """Patch requests.head to return 404."""
    with patch("requests.head") as mock_head:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_head.return_value = mock_resp
        yield mock_head


def test_recon_pipeline_creates_output_directory(tmp_path, mock_engine, mock_requests, mock_requests_head):
    """Running the recon pipeline should create the output directory structure."""
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
            out_dir = tmp_path / "reports" / "example.com" / "test_session"
            out_dir.mkdir(parents=True)
            mock_outdir.return_value = str(out_dir)

            with patch("core.logger.setup_logger"), \
                 patch("core.logger.get_logger") as mock_logger:
                mock_log = MagicMock()
                mock_logger.return_value = mock_log

                from automation.recon_pipeline import run
                run("example.com")

    assert out_dir.exists()


def test_recon_pipeline_generates_html_report(tmp_path, mock_engine, mock_requests, mock_requests_head):
    """After running recon pipeline, an HTML report should be created."""
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
            out_dir = tmp_path / "reports" / "example.com" / "test_session"
            out_dir.mkdir(parents=True)
            # Create a minimal scan file so report builder has something to collect
            (out_dir / "whois.txt").write_text("Domain: example.com")
            mock_outdir.return_value = str(out_dir)

            with patch("core.logger.setup_logger"), \
                 patch("core.logger.get_logger", return_value=MagicMock()):
                from automation.recon_pipeline import run
                report_path = run("example.com")

    assert Path(report_path).exists()
    content = Path(report_path).read_text(encoding="utf-8")
    assert "DARKWIN" in content
