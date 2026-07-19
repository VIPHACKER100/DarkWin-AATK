"""
DARKWIN — Unit Tests | CLI (Darkwin)
"""

import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


def test_cli_invokes_banner(runner):
    from core.darkwin import cli
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "DARKWIN" in result.output


def test_cli_version(runner):
    from core.darkwin import cli
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "1.2.0" in result.output


def test_print_banner_no_crash(runner):
    from core.darkwin import print_banner
    from core import console
    with patch.object(console, "print") as mock_print:
        print_banner()
        assert mock_print.call_count >= 2


def test_cli_run_requires_target(runner):
    from core.darkwin import cli
    result = runner.invoke(cli, ["run"])
    assert result.exit_code != 0


def test_cli_run_requires_mode(runner):
    from core.darkwin import cli
    result = runner.invoke(cli, ["run", "-t", "example.com"])
    assert result.exit_code != 0


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
@patch("core.config_loader.load_config")
def test_cli_run_recon_mode(mock_config, mock_logger, mock_pipeline, runner):
    from core.darkwin import cli
    mock_config.return_value = {"log_dir": "/tmp", "tools": {}}
    mock_pipeline.return_value = None

    result = runner.invoke(cli, ["run", "-t", "example.com", "-m", "recon", "--confirm-scope"])
    assert result.exit_code == 0


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
@patch("core.config_loader.load_config")
def test_cli_run_scan_needs_confirm(mock_config, mock_logger, mock_pipeline, runner):
    from core.darkwin import cli
    mock_config.return_value = {"log_dir": "/tmp", "tools": {}}

    result = runner.invoke(cli, ["run", "-t", "example.com", "-m", "scan"], input="n\n")
    assert result.exit_code == 1


@patch("core.tool_loader.verify_all_tools")
@patch("core.config_loader.load_config")
def test_cli_doctor(mock_config, mock_verify, runner):
    from core.darkwin import cli
    mock_config.return_value = {"tools": {"nmap": "nmap"}}
    mock_verify.return_value = {"nmap": True}

    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0


@patch("core.tool_loader.verify_all_tools")
@patch("core.config_loader.load_config")
def test_cli_doctor_reports_missing(mock_config, mock_verify, runner):
    from core.darkwin import cli
    mock_config.return_value = {"tools": {"amass": "amass"}}
    mock_verify.return_value = {"amass": False}

    result = runner.invoke(cli, ["doctor"])
    assert result.exit_code == 0
