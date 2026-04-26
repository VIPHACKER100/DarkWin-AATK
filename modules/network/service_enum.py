"""
DARKWIN — Network | Service Enumeration
Uses masscan for fast port discovery across all 65535 ports.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Run masscan for rapid service/port discovery.

    Args:
        target:     Target IP or CIDR range.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="service_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/service_enum.log"
    out_file = f"{output_dir}/masscan.txt"

    log.info(f"Starting masscan service enumeration on: {target}")

    engine.run_command(
        f"masscan -p1-65535 {target} --rate=10000 -oG {out_file}",
        log_file=log_file,
        tool_name="masscan",
        target=target,
    )

    log.success(f"Service enumeration complete → {out_file}")
