"""
DARKWIN — Automation | Full Scan Pipeline
Comprehensive security scan pipeline: recon → network → vulnerabilities → fuzzing → report.
"""

from datetime import datetime
from pathlib import Path

from core.config_loader import load_config, get_output_dir
from core.logger import setup_logger, get_logger
from core import engine

from modules.network import port_scanner, service_enum, smb_enum, ftp_enum, ssh_enum
from modules.vulnerabilities.xss import reflected_xss, dom_xss
from modules.vulnerabilities.sqli import sqli_detector, blind_sqli
from modules.vulnerabilities.lfi import lfi_scanner
from modules.vulnerabilities.ssrf import ssrf_tester
from modules.vulnerabilities.rce import rce_scanner
from modules.vulnerabilities.csrf import csrf_detector
from modules.vulnerabilities.idor import idor_scanner
from modules.fuzzing import directory_fuzzer, api_fuzzer, parameter_fuzzer
from modules.reporting import report_builder, html_report, markdown_report
import automation.recon_pipeline as recon_pipeline


def run(target: str) -> str:
    """
    Execute the comprehensive full scan pipeline.

    Stages:
        1. Recon pipeline (subdomain, DNS, WHOIS, URLs, JS)
        2. Network scanning (nmap + masscan + SMB/FTP/SSH)
        3. Vulnerability scanning (XSS, SQLi, LFI, SSRF, RCE, CSRF)
        4. Fuzzing (directories, API, parameters)
        5. Report generation (HTML + Markdown)

    Args:
        target: Target domain or IP.

    Returns:
        Path to the generated HTML report.
    """
    config = load_config()
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = get_output_dir(config, target, session_id)
    log_dir = config.get("log_dir", "logs")
    setup_logger(log_dir=log_dir, tool_name="full_scan_pipeline", target=target)
    log = get_logger(tool_name="full_scan_pipeline", target=target)

    log.info(f"=== FULL SCAN PIPELINE START | Target: {target} | Session: {session_id} ===")

    target_url = f"https://{target}" if not target.startswith("http") else target
    all_urls_file = f"{output_dir}/all_urls.txt"

    # ── Stage 1: Recon ───────────────────────────────────────────────────────
    log.info("[1/5] Running recon pipeline")
    recon_pipeline.run(target, output_dir=output_dir)

    # ── Stage 2: Network Scanning ────────────────────────────────────────────
    log.info("[2/5] Network scanning")
    port_scanner.run(target, output_dir)
    service_enum.run(target, output_dir)
    smb_enum.run(target, output_dir)
    ftp_enum.run(target, output_dir)
    ssh_enum.run(target, output_dir)

    # ── Stage 3: Vulnerability Scanning ─────────────────────────────────────
    log.info("[3/5] Vulnerability scanning")
    if Path(all_urls_file).exists():
        reflected_xss.run(all_urls_file, output_dir)
        dom_xss.run(all_urls_file, output_dir)
    sqli_detector.run(target_url, output_dir)
    blind_sqli.run(target_url, output_dir)
    lfi_scanner.run(f"{target_url}/?page=FUZZ", output_dir)
    ssrf_tester.run(f"{target_url}/?url=FUZZ", output_dir)
    rce_scanner.run(target_url, output_dir)
    csrf_detector.run(target_url, output_dir)
    idor_scanner.run(f"{target_url}/?id=FUZZ", output_dir)

    # ── Stage 4: Fuzzing ─────────────────────────────────────────────────────
    log.info("[4/5] Fuzzing")
    directory_fuzzer.run(target, output_dir)
    api_fuzzer.run(target, output_dir)
    if Path(all_urls_file).exists():
        parameter_fuzzer.run(target_url, output_dir)

    # ── Stage 5: Report ───────────────────────────────────────────────────────
    log.info("[5/5] Generating reports")
    results = report_builder.collect_results(output_dir)
    report_path = html_report.generate(results, output_dir)
    markdown_report.generate(results, output_dir)

    log.success(f"=== FULL SCAN PIPELINE COMPLETE | Report: {report_path} ===")
    return report_path
