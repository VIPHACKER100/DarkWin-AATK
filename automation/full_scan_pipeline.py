"""
DARKWIN — Automation | Full Scan Pipeline
Comprehensive security scan pipeline: recon → network → vulnerabilities → fuzzing → report.
"""

import re
from datetime import datetime
from pathlib import Path

from core.config_loader import load_config, get_output_dir
from core.logger import setup_logger, get_logger
from core import progress as progress_hub
from modules.network import port_scanner, service_enum, smb_enum, ftp_enum, ssh_enum
from modules.vulnerabilities.xss import reflected_xss, dom_xss
from modules.vulnerabilities.sqli import sqli_detector, blind_sqli
from modules.vulnerabilities.lfi import lfi_scanner
from modules.vulnerabilities.ssrf import ssrf_tester
from modules.vulnerabilities.rce import rce_scanner
from modules.vulnerabilities.csrf import csrf_detector
from modules.vulnerabilities.idor import idor_scanner
from modules.fuzzing import directory_fuzzer, api_fuzzer, parameter_fuzzer
from modules.reporting import report_builder, html_report
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
    target = re.sub(r"^https?://", "", target).rstrip("/")
    target_url = f"https://{target}" if not target.startswith("http") else target
    session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = get_output_dir(config, target, session_id)
    log_dir = config.get("log_dir", "logs")
    setup_logger(log_dir=log_dir, tool_name="full_scan_pipeline", target=target)
    log = get_logger(tool_name="full_scan_pipeline", target=target)

    progress_hub.reset()

    log.info(f"=== FULL SCAN PIPELINE START | Target: {target} | Session: {session_id} ===")
    all_urls_file = f"{output_dir}/all_urls.txt"

    # ── Stage 1: Recon (40%) ───────────────────────────────────────────────
    progress_hub.stage("[1/5] Running recon pipeline", 0, log.info)
    recon_pipeline.run(target, output_dir=output_dir, stage_weight=4.0, reset_progress=False)

    # ── Stage 2: Network Scanning (20%) ─────────────────────────────────────
    progress_hub.stage("[2/5] Network scanning", 0, log.info)
    for name, fn in (
        ("nmap port scan", port_scanner.run),
        ("service enumeration", service_enum.run),
        ("SMB enumeration", smb_enum.run),
        ("FTP enumeration", ftp_enum.run),
        ("SSH enumeration", ssh_enum.run),
    ):
        progress_hub.advance(4.0, f"[2/5] {name}")
        fn(target, output_dir)

    # ── Stage 3: Vulnerability Scanning (18%) ────────────────────────────────
    progress_hub.stage("[3/5] Vulnerability scanning", 0, log.info)
    if Path(all_urls_file).exists():
        progress_hub.advance(2.0, "[3/5] reflected XSS")
        reflected_xss.run(all_urls_file, output_dir)
        progress_hub.advance(2.0, "[3/5] DOM XSS")
        dom_xss.run(all_urls_file, output_dir)
    for name, fn in (
        ("SQL injection", sqli_detector.run),
        ("blind SQLi", blind_sqli.run),
        ("LFI scanner", lfi_scanner.run),
        ("SSRF tester", ssrf_tester.run),
        ("RCE scanner", rce_scanner.run),
        ("CSRF detector", csrf_detector.run),
        ("IDOR scanner", idor_scanner.run),
    ):
        progress_hub.advance(2.0, f"[3/5] {name}")
        if name == "LFI scanner":
            fn(f"{target_url}/?page=FUZZ", output_dir)
        elif name == "SSRF tester":
            fn(f"{target_url}/?url=FUZZ", output_dir)
        elif name == "IDOR scanner":
            fn(f"{target_url}/?id=FUZZ", output_dir)
        else:
            fn(target_url, output_dir)

    # ── Stage 4: Fuzzing (12%) ───────────────────────────────────────────────
    progress_hub.stage("[4/5] Fuzzing", 0, log.info)
    progress_hub.advance(4.0, "[4/5] directory fuzzing")
    directory_fuzzer.run(target, output_dir)
    progress_hub.advance(4.0, "[4/5] API fuzzing")
    api_fuzzer.run(target, output_dir)
    if Path(all_urls_file).exists():
        progress_hub.advance(4.0, "[4/5] parameter fuzzing")
        parameter_fuzzer.run(target_url, output_dir)

    # ── Stage 5: Report ───────────────────────────────────────────────────────
    progress_hub.stage("[5/5] Generating reports", 10, log.info)
    results = report_builder.collect_results(output_dir)
    report_path = html_report.generate(results, output_dir)

    progress_hub.set_pct(100, "done")
    log.success(f"=== FULL SCAN PIPELINE COMPLETE | Report: {report_path} ===")
    return report_path
