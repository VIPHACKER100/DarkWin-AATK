"""
DARKWIN — Fuzzing | Directory Fuzzer
Uses ffuf to brute-force hidden directories and files on a target web server.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target: str, output_dir: str, wordlist: str = None) -> None:
    """
    Fuzz for hidden directories and files using ffuf.

    Args:
        target:     Target domain or base URL (without trailing slash).
        output_dir: Directory to write results into.
        wordlist:   Path to directory wordlist. Uses config default if not provided.
    """
    log = get_logger(tool_name="directory_fuzzer", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if wordlist is None:
        config = load_config()
        wordlist = config.get("wordlists", {}).get(
            "directories", "wordlists/SecLists/Discovery/Web-Content/common.txt"
        )

    log_file = f"{output_dir}/directory_fuzzer.log"
    out_file = f"{output_dir}/dir_fuzz.json"

    # Normalise target — strip trailing slash
    target = target.rstrip("/")
    if not target.startswith("http"):
        target = f"https://{target}"

    log.info(f"Starting directory fuzzing on: {target}")

    engine.run_command(
        f'ffuf -u {target}/FUZZ -w "{wordlist}" '
        f"-mc 200,201,301,302,403,405 -o {out_file} -of json -t 50 -silent",
        log_file=log_file,
        tool_name="ffuf-dir",
        target=target,
    )

    log.success(f"Directory fuzzing complete → {out_file}")
