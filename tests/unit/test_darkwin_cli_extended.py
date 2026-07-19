"""
DARKWIN — Unit Tests | CLI (Darkwin) — Extended Coverage
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from click.testing import CliRunner


@pytest.fixture
def runner():
    return CliRunner()


def test_main_calls_cli():
    from core.darkwin import main
    with patch("core.darkwin.cli") as mock_cli:
        main()
        mock_cli.assert_called_once()


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
@patch("core.config_loader.load_config")
def test_cli_run_with_dashboard_flag(mock_config, mock_logger, mock_pipeline, runner):
    from core.darkwin import cli
    mock_config.return_value = {"log_dir": "/tmp", "tools": {}}

    with patch("core.darkwin._start_dashboard"):
        result = runner.invoke(cli, ["run", "-t", "example.com", "-m", "recon", "--confirm-scope", "--dashboard"])
        assert result.exit_code == 0


def test_start_dashboard_import_error():
    from core.darkwin import _start_dashboard
    import importlib
    with patch.dict("sys.modules", {"dashboard.backend.app": None}):
        with pytest.raises(SystemExit):
            _start_dashboard(port=5000)


@patch("core.tool_loader.verify_all_tools")
@patch("core.config_loader.load_config")
def test_cli_doctor_with_fix_linux(mock_config, mock_verify, runner):
    from core.darkwin import cli
    mock_config.return_value = {"tools": {"amass": "amass"}}
    mock_verify.return_value = {"amass": False}

    with patch("subprocess.run") as mock_sub:
        with patch("sys.platform", "linux"):
            result = runner.invoke(cli, ["doctor", "--fix"])
            assert result.exit_code == 0


@patch("core.tool_loader.verify_all_tools")
@patch("core.config_loader.load_config")
def test_cli_doctor_with_fix_non_linux(mock_config, mock_verify, runner):
    from core.darkwin import cli
    mock_config.return_value = {"tools": {"amass": "amass"}}
    mock_verify.return_value = {"amass": False}

    with patch("sys.platform", "darwin"):
        result = runner.invoke(cli, ["doctor", "--fix"])
        assert result.exit_code == 0


@patch("core.tool_loader.verify_all_tools")
@patch("core.config_loader.load_config")
def test_cli_doctor_fix_all_found(mock_config, mock_verify, runner):
    from core.darkwin import cli
    mock_config.return_value = {"tools": {"nmap": "nmap"}}
    mock_verify.return_value = {"nmap": True}

    result = runner.invoke(cli, ["doctor", "--fix"])
    assert result.exit_code == 0


@patch("core.tool_loader.verify_all_tools")
@patch("core.config_loader.load_config")
def test_cli_update(mock_config, mock_verify, runner):
    from core.darkwin import cli
    mock_config.return_value = {"tools": {"nmap": "nmap"}}
    mock_verify.return_value = {"nmap": True}

    with patch("subprocess.run") as mock_sub:
        result = runner.invoke(cli, ["update"])
        assert result.exit_code == 0
        mock_sub.assert_called_once_with(["git", "pull"], check=False)


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
@patch("core.config_loader.load_config")
def test_cli_run_scan_confirmed(mock_config, mock_logger, mock_pipeline, runner):
    from core.darkwin import cli
    mock_config.return_value = {"log_dir": "/tmp", "tools": {}}

    result = runner.invoke(cli, ["run", "-t", "example.com", "-m", "scan"], input="y\n")
    assert result.exit_code == 0
    mock_pipeline.assert_called_once_with("scan", "example.com")


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
@patch("core.config_loader.load_config")
def test_cli_run_bounty_confirmed(mock_config, mock_logger, mock_pipeline, runner):
    from core.darkwin import cli
    mock_config.return_value = {"log_dir": "/tmp", "tools": {}}

    result = runner.invoke(cli, ["run", "-t", "example.com", "-m", "bounty"], input="y\n")
    assert result.exit_code == 0
    mock_pipeline.assert_called_once_with("bounty", "example.com")
