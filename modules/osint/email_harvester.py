"""
DARKWIN — OSINT | Email Harvester
Uses theHarvester to collect email addresses, hostnames, and employee data.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Harvest emails and related OSINT data using theHarvester.

    Args:
        target:     Target domain (e.g., example.com).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="email_harvester", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/email_harvester.log"
    out_base = f"{output_dir}/emails"

    log.info(f"Starting email harvesting for: {target}")

    engine.run_command(
        f"theHarvester -d {target} -l 500 -b all -f {out_base}",
        log_file=log_file,
        tool_name="theHarvester",
        target=target,
    )

    log.success(f"Email harvesting complete → {out_base}.html / {out_base}.xml")
