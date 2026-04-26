"""
DARKWIN — Network | Port Scanner
Full TCP port scan using nmap with service/version detection.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Run a comprehensive nmap port scan against the target.

    Args:
        target:     Target IP or domain.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="port_scanner", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/port_scanner.log"
    out_file = f"{output_dir}/nmap_full.txt"
    xml_out = f"{output_dir}/nmap_full.xml"

    log.info(f"Starting full port scan on: {target}")

    engine.run_command(
        f"nmap -sC -sV -p- --min-rate=1000 {target} "
        f"-oN {out_file} -oX {xml_out}",
        log_file=log_file,
        tool_name="nmap",
        target=target,
    )

    log.success(f"Port scan complete → {out_file}")
