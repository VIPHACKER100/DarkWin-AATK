"""
DARKWIN — Vulnerabilities | XSS | Reflected XSS Scanner
Uses Dalfox to detect reflected XSS vulnerabilities in a list of URLs.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(urls_file: str, output_dir: str) -> None:
    """
    Scan a list of URLs for reflected XSS vulnerabilities using Dalfox.

    Args:
        urls_file:  Path to a file containing one URL per line.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="reflected_xss", target=urls_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if not Path(urls_file).exists():
        log.error(f"URLs file not found: {urls_file}")
        return

    log_file = f"{output_dir}/reflected_xss.log"
    out_file = f"{output_dir}/xss_results.txt"

    log.info(f"Starting reflected XSS scan on URLs from: {urls_file}")

    engine.run_command(
        f"dalfox file {urls_file} -o {out_file} --skip-bav --no-color",
        log_file=log_file,
        tool_name="dalfox",
        target=urls_file,
    )

    log.success(f"Reflected XSS scan complete → {out_file}")
