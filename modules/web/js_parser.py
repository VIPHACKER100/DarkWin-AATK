"""
DARKWIN — Web | JavaScript Parser
Extracts JS files from a target and parses them for endpoints, secrets, and links.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger


def run(target: str, output_dir: str) -> None:
    """
    Discover JavaScript files and extract links/endpoints using subjs and linkfinder.

    Args:
        target:     Target URL or domain.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="js_parser", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    log_file = f"{output_dir}/js_parser.log"
    js_files_out = f"{output_dir}/js_files.txt"
    js_links_out = f"{output_dir}/js_links.txt"
    js_secrets_out = f"{output_dir}/js_secrets.txt"

    log.info(f"Discovering JavaScript files for: {target}")

    # Step 1: Collect JS file URLs
    engine.run_command(
        f"subjs -i {target} | tee {js_files_out}",
        log_file=log_file,
        tool_name="subjs",
        target=target,
    )

    if not Path(js_files_out).exists() or Path(js_files_out).stat().st_size == 0:
        log.warning("No JavaScript files found by subjs.")
        return

    # Step 2: Extract links from JS files
    engine.run_command(
        f"linkfinder -i {js_files_out} -o {js_links_out}",
        log_file=log_file,
        tool_name="linkfinder",
        target=target,
    )

    # Step 3: Search for potential secrets in JS content
    engine.run_command(
        f"cat {js_files_out} | xargs -I{{}} curl -s {{}} | grep -Ei "
        f"'(api_key|apikey|secret|token|password|auth|bearer)\\s*[=:]\\s*[\"\\'][^\"\\']{{8,}}' "
        f"> {js_secrets_out}",
        log_file=log_file,
        tool_name="grep-secrets",
        target=target,
    )

    log.success(
        f"JS parsing complete → {js_files_out}, {js_links_out}, {js_secrets_out}"
    )
