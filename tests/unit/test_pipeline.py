"""
DARKWIN — Unit Tests | Pipeline Router
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from core.pipeline import PIPELINE_MODES


def test_pipeline_modes_has_all_keys():
    assert "recon" in PIPELINE_MODES
    assert "scan" in PIPELINE_MODES
    assert "bounty" in PIPELINE_MODES


def test_pipeline_modes_values_are_module_paths():
    for mode, path in PIPELINE_MODES.items():
        assert isinstance(path, str)
        assert "pipeline" in path


def test_run_pipeline_invalid_mode_exits():
    from core.pipeline import run_pipeline
    with patch.object(sys, "exit", side_effect=SystemExit(1)):
        with pytest.raises(SystemExit):
            run_pipeline("invalid_mode", "example.com")


@patch("importlib.import_module")
def test_run_pipeline_valid_mode_imports_module(mock_import):
    mock_pipeline = MagicMock()
    mock_import.return_value = mock_pipeline

    from core.pipeline import run_pipeline
    run_pipeline("recon", "example.com")

    mock_import.assert_called_once_with("automation.recon_pipeline")
    mock_pipeline.run.assert_called_once_with("example.com")


@patch("importlib.import_module")
def test_run_pipeline_scan_mode(mock_import):
    mock_pipeline = MagicMock()
    mock_import.return_value = mock_pipeline

    from core.pipeline import run_pipeline
    run_pipeline("scan", "192.168.1.1")

    mock_import.assert_called_once_with("automation.full_scan_pipeline")
    mock_pipeline.run.assert_called_once_with("192.168.1.1")


@patch("importlib.import_module")
def test_run_pipeline_bounty_mode(mock_import):
    mock_pipeline = MagicMock()
    mock_import.return_value = mock_pipeline

    from core.pipeline import run_pipeline
    run_pipeline("bounty", "target.com")

    mock_import.assert_called_once_with("automation.bug_bounty_pipeline")
    mock_pipeline.run.assert_called_once_with("target.com")


def test_run_pipeline_mode_case_insensitive():
    from core.pipeline import PIPELINE_MODES
    assert "recon" in PIPELINE_MODES
    assert "RECON".lower() in PIPELINE_MODES


def test_run_pipeline_import_error_exits():
    from core.pipeline import run_pipeline
    with patch("importlib.import_module", side_effect=ImportError("module not found")):
        with patch.object(sys, "exit", side_effect=SystemExit(1)):
            with pytest.raises(SystemExit):
                run_pipeline("recon", "example.com")


def test_run_pipeline_runtime_error_exits():
    from core.pipeline import run_pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.run.side_effect = RuntimeError("boom")
    with patch("importlib.import_module", return_value=mock_pipeline):
        with patch.object(sys, "exit", side_effect=SystemExit(1)):
            with pytest.raises(SystemExit):
                run_pipeline("recon", "example.com")
