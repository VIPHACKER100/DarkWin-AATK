"""
DARKWIN — Automation | Recon Pipeline
Full passive and active reconnaissance pipeline for a target domain.
"""

import re
from datetime import datetime
from pathlib import Path

from core.config_loader import load_config, get_output_dir
from core.logger import setup_logger, get_logger
from core import progress as progress_hub

from modules.recon import (
    subdomain_enum,
    dns_bruteforce,
    reverse_ip,
    whois_lookup,
    asn_lookup,
    github_dorking,
    s3_bucket_scan,
)
from modules.osint import (
    email_harvester,
    metadata_scraper,
    social_media_enum,
    breach_lookup,
)
from modules.cloud import cloud_enum
from modules.web import url_collector, crawler, parameter_finder, js_parser
from modules.reporting import report_builder, html_report


def run(target: str, output_dir: str = None, stage_weight: float = 10.0,
        reset_progress: bool = True) -> str:
    """
    Execute the full recon pipeline against the specified target.

    Stages:
        1. Setup output directory and logger
        2. OSINT (emails, social, breaches)
        3. Cloud discovery (AWS, Azure, GCP)
        4. Subdomain enumeration (subfinder + amass)
        5. DNS bruteforce
        6. ASN / reverse IP / WHOIS lookups
        7. GitHub dorking + S3 bucket scan
        8. URL collection (gau + waybackurls) + web crawl
        9. JS parsing + parameter discovery
        10. HTML report generation

    Args:
        target:              Target domain (e.g., example.com).
        output_dir:          Optional existing output directory.
        stage_weight:        Progress percent each of the 10 stages advances the
                             global bar. Default 10 (standalone totals 100);
                             parent pipelines pass 4 so recon covers 40% of the
                             total scan.
        reset_progress:      Whether to reset the global 0-100 pointer first.

    Returns:
        Path to the generated HTML report.
    """
    target = re.sub(r"^https?://", "", target).rstrip("/")

    config = load_config()
    if not output_dir:
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = get_output_dir(config, target, session_id)

    if reset_progress:
        progress_hub.reset()

    log_dir = config.get("log_dir", "logs")
    setup_logger(log_dir=log_dir, tool_name="recon_pipeline", target=target)
    log = get_logger(tool_name="recon_pipeline", target=target)

    log.info(f"=== RECON PIPELINE START | Target: {target} | Output: {output_dir} ===")

    import concurrent.futures

    # ── Stage 1: OSINT ───────────────────────────────────────────────────────
    progress_hub.stage("[1/10] OSINT gathering (Parallel)", stage_weight, log.info)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        executor.submit(email_harvester.run, target, output_dir)
        executor.submit(metadata_scraper.run, target, output_dir)
        executor.submit(social_media_enum.run, target, output_dir)
        executor.submit(breach_lookup.run, target, output_dir)

    # ── Stage 2: Cloud Discovery ─────────────────────────────────────────────
    progress_hub.stage("[2/10] Cloud discovery", stage_weight, log.info)
    cloud_enum.run(target, output_dir)

    # ── Stage 3: Subdomain Enumeration ──────────────────────────────────────
    progress_hub.stage("[3/10] Subdomain enumeration", stage_weight, log.info)
    subdomain_enum.run(target, output_dir)

    # ── Stage 4: DNS Bruteforce ──────────────────────────────────────────────
    progress_hub.stage("[4/10] DNS bruteforce", stage_weight, log.info)
    wordlist = config.get("wordlists", {}).get("dns", "")
    dns_bruteforce.run(target, output_dir, wordlist=wordlist if wordlist else None)

    # ── Stage 5: Lookups ───────────────────────────────────
    progress_hub.stage("[5/10] ASN, Reverse IP, and WHOIS lookups (Parallel)", stage_weight, log.info)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(asn_lookup.run, target, output_dir)
        executor.submit(reverse_ip.run, target, output_dir)
        executor.submit(whois_lookup.run, target, output_dir)

    # ── Stage 6: GitHub Dorking + S3 Buckets ────────────────────────────────
    progress_hub.stage("[6/10] GitHub dorking & S3 scanning (Parallel)", stage_weight, log.info)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(github_dorking.run, target, output_dir)
        executor.submit(s3_bucket_scan.run, target, output_dir)

    # ── Stage 7: URL Collection ──────────────────────────────────────────────
    progress_hub.stage("[7/10] URL collection (gau + waybackurls)", stage_weight, log.info)
    url_collector.run(target, output_dir)

    # ── Stage 8: Web Crawl ───────────────────────────────────────────────────
    progress_hub.stage("[8/10] Web crawl (katana)", stage_weight, log.info)
    target_url = f"https://{target}" if not target.startswith("http") else target
    crawler.run(target_url, output_dir)

    # ── Stage 9: JS Parsing + Parameter Discovery ────────────────────────────
    progress_hub.stage("[9/10] JS file parsing", stage_weight, log.info)
    js_parser.run(target_url, output_dir)

    all_urls_file = f"{output_dir}/all_urls.txt"
    if Path(all_urls_file).exists():
        log.info("[9/10] Parameter discovery")
        parameter_finder.run(all_urls_file, output_dir)

    # ── Stage 10: Report ─────────────────────────────────────────────────────
    progress_hub.stage("[10/10] Generating reports", stage_weight, log.info)
    results = report_builder.collect_results(output_dir)
    report_path = html_report.generate(results, output_dir)

    progress_hub.set_pct(100, "done")
    log.success(f"=== RECON PIPELINE COMPLETE | Report: {report_path} ===")
    return report_path
