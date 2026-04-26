"""
DARKWIN — Vulnerabilities | IDOR Scanner
Fuzzes for Insecure Direct Object References in URL parameters using ffuf.
"""

from core import engine
from core.logger import get_logger


def run(target_url: str, output_dir: str) -> None:
    """
    Run IDOR scanning against the target URL.
    
    Args:
        target_url: The URL to test (should contain a parameter to fuzz, e.g., ?id=FUZZ).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="idor_scanner", target=target_url)
    
    # Ensure URL has FUZZ marker
    if "FUZZ" not in target_url:
        if "=" in target_url:
            # Try to replace the last parameter value with FUZZ
            base, param = target_url.rsplit("=", 1)
            target_url = f"{base}=FUZZ"
        else:
            log.warning("Target URL for IDOR scan should contain a parameter to fuzz (e.g., ?id=FUZZ).")
            return

    log_file = f"{output_dir}/idor_scanner.log"
    out_file = f"{output_dir}/idor_results.txt"

    log.info(f"Starting IDOR scan on: {target_url}")

    # Using ffuf to iterate through common ID numbers
    # We'll use a range 0-1000 for this basic module
    engine.run_command(
        f"ffuf -u \"{target_url}\" -w <(seq 0 1000) -o {out_file} -of csv -ac -t 50 -silent",
        log_file=log_file,
        tool_name="ffuf-idor",
        target=target_url,
    )

    log.success(f"IDOR scan complete → {out_file}")
