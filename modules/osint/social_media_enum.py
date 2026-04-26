"""
DARKWIN — OSINT | Social Media Enumeration
Uses Sherlock to find social media accounts for a given username or target handle.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Enumerate social media profiles using Sherlock.

    Args:
        target:     Target username or handle to search for.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="social_media_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/social_media_enum.log"
    out_file = f"{output_dir}/social.txt"

    log.info(f"Starting social media enumeration for username: {target}")

    engine.run_command(
        f"sherlock {target} --output {out_file} --print-found",
        log_file=log_file,
        tool_name="sherlock",
        target=target,
    )

    log.success(f"Social media enumeration complete → {out_file}")
