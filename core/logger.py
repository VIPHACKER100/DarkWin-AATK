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

def setup_logger(log_dir: str = "logs", tool_name: str = "darkwin", target: str = "unknown") -> str:
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = str(log_path / f"{session_id}.log")

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

    logger.add(
        log_file,
        format=LOG_FORMAT,
        level="DEBUG",
        rotation="50 MB",
        retention="30 days",
        encoding="utf-8",
    )

    return log_file


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
