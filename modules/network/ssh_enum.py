"""
DARKWIN — Network | SSH Enumeration
Uses nmap SSH scripts to discover authentication methods and supported algorithms.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Enumerate SSH service using nmap scripts.

    Args:
        target:     Target IP or hostname.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="ssh_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/ssh_enum.log"
    out_file = f"{output_dir}/ssh_enum.txt"

    log.info(f"Starting SSH enumeration on: {target}")

    engine.run_command(
        f"nmap -sV --script ssh-auth-methods,ssh2-enum-algos,ssh-hostkey -p 22 {target} -oN {out_file}",
        log_file=log_file,
        tool_name="nmap-ssh",
        target=target,
    )

    log.success(f"SSH enumeration complete → {out_file}")
