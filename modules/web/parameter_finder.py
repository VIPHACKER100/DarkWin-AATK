"""
DARKWIN — Web | Parameter Finder
Uses Arjun to discover hidden HTTP parameters in target URLs.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(urls_file: str, output_dir: str) -> None:
    """
    Discover hidden parameters for URLs listed in an input file.

    Args:
        urls_file:  Path to a file containing one URL per line.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="parameter_finder", target=urls_file)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if not Path(urls_file).exists():
        log.error(f"URLs file not found: {urls_file}")
        return

    log_file = f"{output_dir}/parameter_finder.log"
    out_file = f"{output_dir}/params.txt"

    log.info(f"Starting parameter discovery from: {urls_file}")

    engine.run_command(
        f"arjun -i {urls_file} -oT {out_file} -t 10 --passive",
        log_file=log_file,
        tool_name="arjun",
        target=urls_file,
    )

    log.success(f"Parameter discovery complete → {out_file}")
