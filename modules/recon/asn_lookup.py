"""
DARKWIN — Recon | ASN Lookup
Discover the AS number/owner for a target IP, or the ASNs behind a domain.

Previously this module dumped raw whois(radb) replies plus whatever HTML
bgp.he.net served (including "404 page not found") straight into asn.txt.
Now it queries the HackerTarget aslookup API and only falls back to a parsed
radb whois, so the output file is clean data instead of page fragments.
"""

import shlex
import subprocess
from pathlib import Path

import requests

from core.logger import get_logger

API_URL = "https://api.hackertarget.com/aslookup/"


def run(target: str, output_dir: str) -> None:
    """
    Perform an ASN lookup for the target and write clean results to asn.txt.

    Args:
        target:     Target IP address or domain.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="asn_lookup", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    out_file = f"{output_dir}/asn.txt"
    rows = _api_aslookup(target, log)
    if not rows:
        rows = _radb_aslookup(target, log)

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# ASN Lookup — {target}\n")
        if rows:
            f.write("IP,ASN,Owner\n")
            for ip, asn, owner in rows:
                f.write(f"{ip},{asn},{owner or '-'}\n")
        else:
            f.write("# No ASN information found for this target.\n")

    log.success(f"ASN lookup complete ({len(rows)} record(s)) → {out_file}")


def _api_aslookup(target: str, log) -> list:
    """Query HackerTarget aslookup (CSV lines: ip,owner,asn,route,country)."""
    rows = []
    try:
        resp = requests.get(API_URL, params={"q": target}, timeout=20)
        if resp.status_code != 200 or not resp.text.strip():
            log.warning(f"HackerTarget aslookup returned status {resp.status_code}")
            return []
        for line in resp.text.splitlines():
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3 and parts[0] and parts[1]:
                rows.append((parts[0], parts[2], parts[1]))
        log.success(f"HackerTarget aslookup returned {len(rows)} record(s)")
    except requests.RequestException as e:
        log.warning(f"HackerTarget aslookup request failed: {e}")
    return rows


def _radb_aslookup(target: str, log) -> list:
    """Fallback: parse ORIGIN lines from an RIPE-style radb whois query."""
    rows = []
    cmd = shlex.split(f"whois -h whois.radb.net {target}")
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as e:
        log.warning(f"radb whois unavailable: {e}")
        return []

    asn, owner, seen = None, None, set()
    for line in (proc.stdout or "").splitlines():
        low = line.lower()
        if low.startswith("origin:"):
            asn = line.split(":", 1)[1].strip().upper()
            key = (asn, owner)
            if asn and key not in seen:
                seen.add(key)
                rows.append((target, asn, owner or ''))
        elif low.startswith(("descr:", "as-name:")):
            owner = line.split(":", 1)[1].strip() or owner
    if rows:
        log.success(f"Parsed {len(rows)} ASN record(s) via radb whois")
    return rows