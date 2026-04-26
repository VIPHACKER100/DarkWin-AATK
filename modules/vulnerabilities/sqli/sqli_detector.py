"""
DARKWIN — Vulnerabilities | SQLi | SQL Injection Detector
Uses sqlmap to detect SQL injection vulnerabilities in a target URL.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target_url: str, output_dir: str) -> None:
    """
    Detect SQL injection vulnerabilities using sqlmap.

    Args:
        target_url: URL to test (may include GET parameters).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="sqli_detector", target=target_url)
    sqli_dir = f"{output_dir}/sqlmap"
    Path(sqli_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/sqli_detector.log"

    log.info(f"Starting SQLi detection on: {target_url}")

    engine.run_command(
        f'sqlmap -u "{target_url}" --batch --level=3 --risk=2 '
        f"-o --output-dir={sqli_dir} --forms --crawl=2",
        log_file=log_file,
        tool_name="sqlmap",
        target=target_url,
    )

    log.success(f"SQLi detection complete → {sqli_dir}")
