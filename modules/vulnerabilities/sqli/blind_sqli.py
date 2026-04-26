"""
DARKWIN — Vulnerabilities | SQLi | Blind SQL Injection
Uses sqlmap with time-based blind technique to detect blind SQLi.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target_url: str, output_dir: str) -> None:
    """
    Detect blind SQL injection using sqlmap's time-based technique.

    Args:
        target_url: URL to test for blind SQLi.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="blind_sqli", target=target_url)
    blind_dir = f"{output_dir}/blind_sqli"
    Path(blind_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/blind_sqli.log"

    log.info(f"Starting blind SQLi scan on: {target_url}")

    engine.run_command(
        f'sqlmap -u "{target_url}" --technique=T --batch '
        f"--time-sec=5 --output-dir={blind_dir}",
        log_file=log_file,
        tool_name="sqlmap-blind",
        target=target_url,
    )

    log.success(f"Blind SQLi scan complete → {blind_dir}")
