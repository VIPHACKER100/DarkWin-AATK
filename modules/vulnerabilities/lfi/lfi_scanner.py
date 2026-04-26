"""
DARKWIN — Vulnerabilities | LFI | LFI Scanner
Uses ffuf with a LFI payload wordlist to detect Local File Inclusion vulnerabilities.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target_url: str, output_dir: str, wordlist: str = None) -> None:
    """
    Fuzz for Local File Inclusion vulnerabilities using ffuf.

    Args:
        target_url: Target URL with FUZZ placeholder (e.g., https://example.com/page?file=FUZZ).
        output_dir: Directory to write results into.
        wordlist:   Path to LFI payload wordlist. Uses config default if not provided.
    """
    log = get_logger(tool_name="lfi_scanner", target=target_url)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if wordlist is None:
        config = load_config()
        wordlist = config.get("wordlists", {}).get(
            "lfi", "wordlists/PayloadsAllTheThings/File Inclusion/Intruder/Linux-Path-traversal.txt"
        )

    log_file = f"{output_dir}/lfi_scanner.log"
    out_file = f"{output_dir}/lfi.json"

    log.info(f"Starting LFI scan on: {target_url}")

    # Ensure FUZZ placeholder is in URL
    if "FUZZ" not in target_url:
        target_url = f"{target_url}FUZZ"

    engine.run_command(
        f'ffuf -u "{target_url}" -w "{wordlist}" '
        f'-o {out_file} -of json -mc 200 -fs 0',
        log_file=log_file,
        tool_name="ffuf-lfi",
        target=target_url,
    )

    log.success(f"LFI scan complete → {out_file}")
