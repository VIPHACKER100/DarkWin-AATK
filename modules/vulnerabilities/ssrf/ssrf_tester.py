"""
DARKWIN — Vulnerabilities | SSRF | SSRF Tester
Uses ffuf with SSRF payloads to detect Server-Side Request Forgery vulnerabilities.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target_url: str, output_dir: str, wordlist: str = None) -> None:
    """
    Test for SSRF vulnerabilities using ffuf.

    Args:
        target_url: Target URL with FUZZ placeholder for the SSRF payload position.
        output_dir: Directory to write results into.
        wordlist:   Path to SSRF payload wordlist. Uses config default if not provided.
    """
    log = get_logger(tool_name="ssrf_tester", target=target_url)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if wordlist is None:
        config = load_config()
        wordlist = config.get("wordlists", {}).get(
            "ssrf",
            "wordlists/PayloadsAllTheThings/Server Side Request Forgery/Intruder/List-of-SSRFs.txt",
        )

    log_file = f"{output_dir}/ssrf_tester.log"
    out_file = f"{output_dir}/ssrf.json"

    log.info(f"Starting SSRF test on: {target_url}")

    if "FUZZ" not in target_url:
        target_url = f"{target_url}FUZZ"

    engine.run_command(
        f'ffuf -u "{target_url}" -w "{wordlist}" '
        f'-o {out_file} -of json -mc 200,301,302,307,400,403',
        log_file=log_file,
        tool_name="ffuf-ssrf",
        target=target_url,
    )

    log.success(f"SSRF test complete → {out_file}")
