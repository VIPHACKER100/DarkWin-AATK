"""
DARKWIN — Vulnerabilities | CSRF | CSRF Detector
Uses Nuclei with CSRF templates to detect Cross-Site Request Forgery vulnerabilities.
"""

from pathlib import Path
from core import engine
from core.logger import get_logger
from core.config_loader import load_config


def run(target_url: str, output_dir: str) -> None:
    """
    Detect CSRF vulnerabilities using Nuclei's CSRF template collection.

    Args:
        target_url: Target URL to scan.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="csrf_detector", target=target_url)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    config = load_config()
    templates_dir = config.get("nuclei_templates", "nuclei-templates")

    log_file = f"{output_dir}/csrf_detector.log"
    out_file = f"{output_dir}/csrf.txt"

    log.info(f"Starting CSRF detection on: {target_url}")

    engine.run_command(
        f"nuclei -u {target_url} -t {templates_dir}/vulnerabilities/csrf/ "
        f"-o {out_file} -silent",
        log_file=log_file,
        tool_name="nuclei-csrf",
        target=target_url,
    )

    log.success(f"CSRF detection complete → {out_file}")
