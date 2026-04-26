"""
DARKWIN — Recon | DNS Bruteforce
Uses dnsrecon to brute-force DNS records for a target domain.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target: str, output_dir: str, wordlist: str = None) -> None:
    """
    Brute-force DNS subdomains using dnsrecon.

    Args:
        target:     Target domain.
        output_dir: Directory to write results into.
        wordlist:   Path to DNS wordlist. Uses config default if not provided.
    """
    log = get_logger(tool_name="dns_bruteforce", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if wordlist is None:
        config = load_config()
        wordlist = config.get("wordlists", {}).get(
            "dns", "wordlists/SecLists/Discovery/DNS/subdomains-top1million-110000.txt"
        )

    log_file = f"{output_dir}/dns_bruteforce.log"
    xml_out = f"{output_dir}/dns_brute.xml"
    csv_out = f"{output_dir}/dns_brute.csv"

    log.info(f"Starting DNS bruteforce on: {target} with wordlist: {wordlist}")

    engine.run_command(
        f"dnsrecon -d {target} -D {wordlist} -t brt -x {xml_out} --csv {csv_out}",
        log_file=log_file,
        tool_name="dnsrecon",
        target=target,
    )

    log.success(f"DNS bruteforce complete → {xml_out}")
