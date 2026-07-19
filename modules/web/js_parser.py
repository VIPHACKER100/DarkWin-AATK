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
    url = target if target.startswith("http") else f"https://{target}"
    engine.run_command(
        f"subjs -i {url} | tee {js_files_out}",
        log_file=log_file,
        tool_name="subjs",
        target=target,
    )

    if not Path(js_files_out).exists() or Path(js_files_out).stat().st_size == 0:
        log.warning("No JavaScript files found by subjs.")
        return

    # Step 2: Extract links from JS files via direct URL or file
    if Path(js_files_out).stat().st_size > 0:
        first_js = Path(js_files_out).read_text(encoding="utf-8").splitlines()[0].strip()
        engine.run_command(
            f"linkfinder -i {first_js} -o cli > {js_links_out}",
            log_file=log_file,
            tool_name="linkfinder",
            target=target,
        )

    # Step 3: Search for potential secrets in JS files
    grep_pattern = r'(api_key|apikey|secret|token|password|auth|bearer)\s*[=:]\s*["'"'"'][^"'"'"']{8,}'
    if Path(js_files_out).exists() and Path(js_files_out).stat().st_size > 0:
        for js_url in Path(js_files_out).read_text(encoding="utf-8").splitlines():
            import subprocess
            try:
                result = subprocess.run(
                    ["curl", "-s", js_url.strip()],
                    capture_output=True, text=True, timeout=15,
                )
                matches = [l for l in result.stdout.splitlines() if __import__('re').search(grep_pattern, l)]
                if matches:
                    with open(js_secrets_out, "a", encoding="utf-8") as f:
                        f.write(f"--- {js_url} ---\n" + "\n".join(matches) + "\n")
            except Exception:
                pass

    log.success(
        f"JS parsing complete → {js_files_out}, {js_links_out}, {js_secrets_out}"
    )
