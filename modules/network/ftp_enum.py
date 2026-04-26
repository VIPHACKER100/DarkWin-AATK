"""
DARKWIN — Network | FTP Enumeration
Uses nmap FTP scripts to detect anonymous login and FTP bounce vulnerabilities.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Enumerate FTP service using nmap scripts.

    Args:
        target:     Target IP or hostname.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="ftp_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/ftp_enum.log"
    out_file = f"{output_dir}/ftp_enum.txt"

    log.info(f"Starting FTP enumeration on: {target}")

    engine.run_command(
        f"nmap -sV --script ftp-anon,ftp-bounce,ftp-brute -p 21 {target} -oN {out_file}",
        log_file=log_file,
        tool_name="nmap-ftp",
        target=target,
    )

    log.success(f"FTP enumeration complete → {out_file}")
