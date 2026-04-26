"""
DARKWIN — Config Loader
Reads and parses the core config.yaml file.
"""

import os
import yaml
from pathlib import Path


def load_config(path: str = None) -> dict:
    """
    Load and parse the DARKWIN configuration YAML file.

    Args:
        path: Explicit path to config.yaml. Defaults to core/config.yaml
              relative to the project root.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    if path is None:
        # Resolve relative to this file's location (core/)
        base_dir = Path(__file__).parent
        path = base_dir / "config.yaml"

    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"[DARKWIN] Config file not found at: {config_path.resolve()}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        raise ValueError("[DARKWIN] Config file is malformed — expected a YAML mapping.")

    return config


def get_output_dir(config: dict, target: str, session_id: str) -> str:
    """
    Construct and create the timestamped output directory for a scan session.

    Args:
        config: Loaded config dictionary.
        target:  Target domain/IP.
        session_id: Timestamp string used as the folder name.

    Returns:
        Absolute path string to the output directory.
    """
    base = config.get("output_dir", "reports")
    output_dir = Path(base) / target / session_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return str(output_dir)
