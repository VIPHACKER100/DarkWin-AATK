"""
DARKWIN — Vulnerabilities | RCE | RCE Scanner
Uses Nuclei with RCE templates to detect Remote Code Execution vulnerabilities.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target_url: str, output_dir: str) -> None:
    """
    Scan for RCE vulnerabilities using Nuclei's RCE template collection.

    Args:
        target_url: Target URL to scan.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="rce_scanner", target=target_url)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    config = load_config()
    templates_dir = config.get("nuclei_templates", "nuclei-templates")

    log_file = f"{output_dir}/rce_scanner.log"
    out_file = f"{output_dir}/rce.txt"

    log.info(f"Starting RCE scan on: {target_url}")

    engine.run_command(
        f"nuclei -u {target_url} -t {templates_dir}/rce/ "
        f"-o {out_file} -severity high,critical -silent",
        log_file=log_file,
        tool_name="nuclei-rce",
        target=target_url,
    )

    log.success(f"RCE scan complete → {out_file}")
