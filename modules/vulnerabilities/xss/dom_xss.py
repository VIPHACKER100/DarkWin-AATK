"""
DARKWIN — Vulnerabilities | XSS | DOM XSS Scanner
Uses kxss to detect potential DOM XSS sinks in a list of URLs.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(urls_file: str, output_dir: str) -> None:
    """
    Scan for DOM XSS sinks using kxss.

    Args:
        urls_file:  Path to a file containing one URL per line.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="dom_xss", target=urls_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if not Path(urls_file).exists():
        log.error(f"URLs file not found: {urls_file}")
        return

    log_file = f"{output_dir}/dom_xss.log"
    out_file = f"{output_dir}/dom_xss.txt"

    log.info(f"Starting DOM XSS scan from: {urls_file}")

    engine.run_command(
        f"kxss < {urls_file} | tee {out_file}",
        log_file=log_file,
        tool_name="kxss",
        target=urls_file,
    )

    log.success(f"DOM XSS scan complete → {out_file}")
