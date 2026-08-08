"""
DARKWIN — Automation | Bug Bounty Pipeline
Optimised pipeline for bug bounty hunting: recon → nuclei → XSS/SQLi → screenshots → report.
"""

import re
from datetime import datetime
from pathlib import Path

from core.config_loader import load_config, get_output_dir
from core.logger import setup_logger, get_logger
from core import engine
from core import progress as progress_hub

from modules.vulnerabilities.xss import reflected_xss
from modules.vulnerabilities.sqli import sqli_detector
from modules.reporting import report_builder, html_report
import automation.recon_pipeline as recon_pipeline


def run(target: str) -> str:
    """
    Execute the bug-bounty-optimised pipeline.

    Stages:
        1. Recon pipeline
        2. Nuclei full scan
        3. Targeted vuln scan (XSS + SQLi)
        4. Screenshots with gowitness
        5. HTML report generation

    Args:
        target: Target domain.

    Returns:
        Path to the generated HTML report.
    """
    config = load_config()
    target = re.sub(r"^https?://", "", target).rstrip("/")
    target_url = f"https://{target}" if not target.startswith("http") else target
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = get_output_dir(config, target, session_id)
    log_dir = config.get("log_dir", "logs")
    setup_logger(log_dir=log_dir, tool_name="bug_bounty_pipeline", target=target)
    log = get_logger(tool_name="bug_bounty_pipeline", target=target)

    progress_hub.reset()

    log.info(f"=== BUG BOUNTY PIPELINE START | Target: {target} | Session: {session_id} ===")
    all_urls_file = f"{output_dir}/all_urls.txt"
    subdomains_file = f"{output_dir}/subdomains_all.txt"
    screenshots_dir = f"{output_dir}/screenshots"
    templates_dir = config.get("nuclei_templates", "nuclei-templates")

    # ── Stage 1: Recon (40%) ───────────────────────────────────────────────
    progress_hub.stage("[1/5] Running recon pipeline", 0, log.info)
    recon_pipeline.run(target, output_dir=output_dir, stage_weight=4.0, reset_progress=False)

    # ── Stage 2: Nuclei Full Scan (30%) ────────────────────────────────────
    progress_hub.stage("[2/5] Running Nuclei full template scan", 15, log.info)
    nuclei_out = f"{output_dir}/nuclei.txt"
    engine.run_command(
        f"nuclei -u {target_url} -t {templates_dir}/ "
        f"-o {nuclei_out} -severity medium,high,critical -silent",
        log_file=f"{output_dir}/nuclei.log",
        tool_name="nuclei",
        target=target,
    )
    progress_hub.advance(15, "[2/5] Nuclei finished")

    # ── Stage 3: Targeted Vuln Scans (10%) ───────────────────────────────────
    progress_hub.stage("[3/5] Targeted vulnerability scans (XSS + SQLi)", 0, log.info)
    if Path(all_urls_file).exists():
        progress_hub.advance(5, "[3/5] reflected XSS")
        reflected_xss.run(all_urls_file, output_dir)
    else:
        progress_hub.advance(5, "[3/5] no URLs — skipping XSS")
    progress_hub.advance(5, "[3/5] SQL injection")
    sqli_detector.run(target_url, output_dir)

    # ── Stage 4: Screenshots (15%) ───────────────────────────────────────────
    progress_hub.stage("[4/5] Taking screenshots with gowitness", 5, log.info)
    Path(screenshots_dir).mkdir(parents=True, exist_ok=True)
    if Path(subdomains_file).exists():
        engine.run_command(
            f"gowitness file -f {subdomains_file} --dest {screenshots_dir} "
            f"--timeout 10",
            log_file=f"{output_dir}/gowitness.log",
            tool_name="gowitness",
            target=target,
        )
    progress_hub.advance(10, "[4/5] Screenshots finished")

    # ── Stage 5: Report (5%) ─────────────────────────────────────────────────
    progress_hub.stage("[5/5] Generating reports", 5, log.info)
    results = report_builder.collect_results(output_dir)
    report_path = html_report.generate(results, output_dir)

    progress_hub.set_pct(100, "done")
    log.success(f"=== BUG BOUNTY PIPELINE COMPLETE | Report: {report_path} ===")
    return report_path
