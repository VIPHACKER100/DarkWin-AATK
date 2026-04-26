"""
DARKWIN — Unit Tests | Config Loader
"""

import pytest
import tempfile
import yaml
from pathlib import Path


def _write_config(data: dict, path: Path):
    with open(path, "w") as f:
        yaml.dump(data, f)


def test_load_config_returns_dict(tmp_path):
    from core.config_loader import load_config
    config_path = tmp_path / "config.yaml"
    _write_config({"version": "1.0.0", "output_dir": "reports", "log_dir": "logs",
                   "default_threads": 5, "tools": {"nmap": "nmap"}}, config_path)
    config = load_config(str(config_path))
    assert isinstance(config, dict)


def test_load_config_required_keys(tmp_path):
    from core.config_loader import load_config
    config_path = tmp_path / "config.yaml"
    _write_config({
        "version": "1.0.0",
        "output_dir": "reports",
        "log_dir": "logs",
        "default_threads": 10,
        "tools": {"subfinder": "subfinder", "nmap": "nmap"},
        "wordlists": {"directories": "wordlists/common.txt"},
    }, config_path)
    config = load_config(str(config_path))
    for key in ["version", "output_dir", "log_dir", "default_threads", "tools"]:
        assert key in config, f"Missing expected key: {key}"


def test_load_config_missing_file():
    from core.config_loader import load_config
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.yaml")


def test_get_output_dir_creates_directory(tmp_path):
    from core.config_loader import get_output_dir
    config = {"output_dir": str(tmp_path / "reports")}
    out = get_output_dir(config, "example.com", "2025-01-01_12-00-00")
    assert Path(out).exists()
    assert "example.com" in out
