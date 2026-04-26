"""
DARKWIN — Network | SMB Enumeration
Uses enum4linux to enumerate SMB shares, users, and policies.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Enumerate SMB services using enum4linux.

    Args:
        target:     Target IP address.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="smb_enum", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/smb_enum.log"
    out_file = f"{output_dir}/smb_enum.txt"

    log.info(f"Starting SMB enumeration on: {target}")

    engine.run_command(
        f"enum4linux -a {target} > {out_file}",
        log_file=log_file,
        tool_name="enum4linux",
        target=target,
    )

    log.success(f"SMB enumeration complete → {out_file}")
