"""
DARKWIN — Fuzzing | Parameter Fuzzer
Uses wfuzz to brute-force GET/POST parameters on a target URL.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target_url: str, output_dir: str, wordlist: str = None) -> None:
    """
    Fuzz URL parameters using wfuzz.

    Args:
        target_url: Target URL with FUZZ placeholder for the parameter name position.
        output_dir: Directory to write results into.
        wordlist:   Path to parameter wordlist. Uses config default if not provided.
    """
    log = get_logger(tool_name="parameter_fuzzer", target=target_url)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if wordlist is None:
        config = load_config()
        wordlist = config.get("wordlists", {}).get(
            "parameters",
            "wordlists/SecLists/Discovery/Web-Content/burp-parameter-names.txt",
        )

    log_file = f"{output_dir}/parameter_fuzzer.log"
    out_file = f"{output_dir}/param_fuzz.txt"

    if "FUZZ" not in target_url:
        target_url = f"{target_url}?FUZZ=test"

    log.info(f"Starting parameter fuzzing on: {target_url}")

    engine.run_command(
        f'wfuzz -c -w "{wordlist}" --hc 404 -o raw "{target_url}" > {out_file}',
        log_file=log_file,
        tool_name="wfuzz",
        target=target_url,
    )

    log.success(f"Parameter fuzzing complete → {out_file}")
