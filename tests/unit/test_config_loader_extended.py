"""
DARKWIN — Unit Tests | Config Loader (Extended)
"""

import pytest
import yaml
from pathlib import Path


def test_load_config_malformed_yaml(tmp_path):
    from core.config_loader import load_config
    config_path = tmp_path / "bad.yaml"
    config_path.write_text("- item1\n- item2\n")

    with pytest.raises(ValueError):
        load_config(str(config_path))


def test_get_output_dir_default_base(tmp_path):
    from core.config_loader import get_output_dir
    config = {}
    out = get_output_dir(config, "example.com", "session1")
    expected = Path("reports") / "example.com" / "session1"
    assert Path(out) == expected


def test_get_output_dir_custom_base(tmp_path):
    from core.config_loader import get_output_dir
    config = {"output_dir": str(tmp_path / "custom_reports")}
    out = get_output_dir(config, "target.com", "s1")
    expected = tmp_path / "custom_reports" / "target.com" / "s1"
    assert Path(out) == expected
    assert Path(out).exists()


def test_load_config_preserves_all_keys(tmp_path):
    from core.config_loader import load_config
    config_path = tmp_path / "config.yaml"
    data = {
        "version": "2.0.0",
        "output_dir": "/tmp/reports",
        "log_dir": "/tmp/logs",
        "default_threads": 8,
        "tools": {"nmap": "nmap", "subfinder": "subfinder"},
        "wordlists": {"directories": "common.txt", "dns": "dns.txt"},
        "api_keys": {"github_token": "ghp_xxx", "hibp_api_key": "key"},
        "nuclei_templates": "nuclei-templates",
    }
    with open(config_path, "w") as f:
        yaml.dump(data, f)

    config = load_config(str(config_path))
    assert config == data


def test_load_config_default_path():
    from core.config_loader import load_config
    from pathlib import Path
    default_path = Path(__file__).parent.parent.parent / "core" / "config.yaml"
    if default_path.exists():
        config = load_config()
        assert isinstance(config, dict)
    else:
        with pytest.raises(FileNotFoundError):
            load_config()


def test_load_config_empty_yaml_raises(tmp_path):
    from core.config_loader import load_config
    config_path = tmp_path / "empty.yaml"
    config_path.write_text("")

    with pytest.raises(ValueError):
        load_config(str(config_path))
