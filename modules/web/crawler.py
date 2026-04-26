"""
DARKWIN — Web | Crawler
Uses Katana to crawl a target web application and collect all discovered URLs.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Crawl a target web application using Katana.

    Args:
        target:     Target URL (e.g., https://example.com).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="crawler", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/crawler.log"
    out_file = f"{output_dir}/crawl.txt"

    log.info(f"Starting web crawl for: {target}")

    engine.run_command(
        f"katana -u {target} -o {out_file} -jc -kf all -d 5 -silent",
        log_file=log_file,
        tool_name="katana",
        target=target,
    )

    log.success(f"Web crawl complete → {out_file}")
