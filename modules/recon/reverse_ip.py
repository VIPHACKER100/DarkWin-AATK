"""
DARKWIN — Recon | Reverse IP Lookup
Discovers other domains hosted on the same IP address.
"""

import requests
from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Perform reverse IP lookup using HackerTarget API and hakrevdns.

    Args:
        target:     Target IP address or domain.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="reverse_ip", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/reverse_ip.log"
    out_file = f"{output_dir}/reverse_ip.txt"

    log.info(f"Starting reverse IP lookup for: {target}")

    # Method 1: HackerTarget API
    try:
        api_url = f"https://api.hackertarget.com/reverseiplookup/?q={target}"
        response = requests.get(api_url, timeout=15)
        if response.status_code == 200:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(f"# Reverse IP Lookup — {target}\n")
                f.write(f"# Source: HackerTarget API\n\n")
                f.write(response.text)
            log.success(f"HackerTarget API returned results → {out_file}")
        else:
            log.warning(f"HackerTarget API returned status {response.status_code}")
    except requests.RequestException as e:
        log.error(f"HackerTarget API request failed: {e}")

    # Method 2: hakrevdns (if installed)
    engine.run_command(
        f"hakrevdns -d {target} >> {out_file}",
        log_file=log_file,
        tool_name="hakrevdns",
        target=target,
    )

    log.success(f"Reverse IP lookup complete → {out_file}")
