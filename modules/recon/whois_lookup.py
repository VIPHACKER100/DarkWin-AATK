"""
DARKWIN — Recon | WHOIS Lookup
Retrieves WHOIS registration data for a target domain.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Perform WHOIS lookup and save registration data.

    Args:
        target:     Target domain or IP address.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="whois_lookup", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/whois_lookup.log"
    out_file = f"{output_dir}/whois.txt"

    log.info(f"Starting WHOIS lookup for: {target}")

    engine.run_command(
        f"whois {target} > {out_file}",
        log_file=log_file,
        tool_name="whois",
        target=target,
    )

    log.success(f"WHOIS lookup complete → {out_file}")
