"""
DARKWIN — Fuzzing | API Fuzzer
Uses ffuf to discover hidden API endpoints.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target: str, output_dir: str, wordlist: str = None) -> None:
    """
    Fuzz API endpoint paths using ffuf.

    Args:
        target:     Target domain (e.g., example.com).
        output_dir: Directory to write results into.
        wordlist:   Path to API wordlist. Uses config default if not provided.
    """
    log = get_logger(tool_name="api_fuzzer", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if wordlist is None:
        config = load_config()
        wordlist = config.get("wordlists", {}).get(
            "directories", "wordlists/SecLists/Discovery/Web-Content/common.txt"
        )

    log_file = f"{output_dir}/api_fuzzer.log"
    out_file = f"{output_dir}/api_fuzz.json"

    target = target.rstrip("/")
    if not target.startswith("http"):
        target = f"https://{target}"

    log.info(f"Starting API endpoint fuzzing on: {target}")

    engine.run_command(
        f'ffuf -u {target}/api/FUZZ -w "{wordlist}" '
        f"-mc all -o {out_file} -of json -t 40 -silent",
        log_file=log_file,
        tool_name="ffuf-api",
        target=target,
    )

    log.success(f"API fuzzing complete → {out_file}")
