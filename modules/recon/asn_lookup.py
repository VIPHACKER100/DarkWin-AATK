"""
DARKWIN — Recon | ASN Lookup
Performs ASN/BGP lookups to identify IP ranges owned by a target organisation.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Query RADB whois for ASN/BGP information.

    Args:
        target:     Target domain, IP, or organisation name.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="asn_lookup", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/asn_lookup.log"
    out_file = f"{output_dir}/asn.txt"

    log.info(f"Starting ASN lookup for: {target}")

    engine.run_command(
        f"whois -h whois.radb.net {target} > {out_file}",
        log_file=log_file,
        tool_name="whois-asn",
        target=target,
    )

    # Also query bgp.he.net via curl if available
    engine.run_command(
        f"curl -s https://bgp.he.net/dns/{target} >> {out_file}",
        log_file=log_file,
        tool_name="bgp-he-net",
        target=target,
    )

    log.success(f"ASN lookup complete → {out_file}")
