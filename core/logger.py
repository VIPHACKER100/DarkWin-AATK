"""
DARKWIN — Logger
Structured, per-session logging with loguru and rich integration.
"""

import sys
from datetime import datetime
from pathlib import Path
from loguru import logger

# Log format constant — used across all modules
LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{extra[tool_name]}</cyan> | "
    "<magenta>{extra[target]}</magenta> | "
    "{message}"
)

_session_id: str = ""
_log_file: str = ""


def get_session_id() -> str:
    """Return the current session ID (timestamp string)."""
    return _session_id


def get_log_file() -> str:
    """Return the path to the current session log file."""
    return _log_file


def setup_logger(log_dir: str = "logs", tool_name: str = "darkwin", target: str = "unknown") -> str:
    """
    Configure the loguru logger for a new scan session.

    Creates a timestamped log file at {log_dir}/{session_id}.log.
    Binds tool_name and target to all log records via extra context.

    Args:
        log_dir:   Directory to write session logs into.
        tool_name: Name of the active tool/module for log context.
        target:    Target being scanned.

    Returns:
        Path to the session log file.
    """
    global _session_id, _log_file

    _session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    _log_file = str(log_path / f"{_session_id}.log")

    # Remove default loguru sink
    logger.remove()

    # Custom SUCCESS level (green, level 25 between INFO=20 and WARNING=30)
    try:
        logger.level("SUCCESS", no=25, color="<green>", icon="✓")
    except ValueError:
        pass  # Already registered

    # Console sink — pretty colored output
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level="DEBUG",
        colorize=True,
    )

    # File sink — machine-readable logs
    logger.add(
        _log_file,
        format=LOG_FORMAT,
        level="DEBUG",
        rotation="50 MB",
        retention="30 days",
        encoding="utf-8",
    )

    return _log_file


def get_logger(tool_name: str = "darkwin", target: str = "unknown"):
    """
    Return a logger instance bound with tool_name and target context.

    Args:
        tool_name: Module or tool producing the log entry.
        target:    Target host/domain being processed.

    Returns:
        Bound loguru logger.
    """
    return logger.bind(tool_name=tool_name, target=target)
