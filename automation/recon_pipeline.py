"""
DARKWIN — Automation | Recon Pipeline
Full passive and active reconnaissance pipeline for a target domain.
"""

from datetime import datetime
from pathlib import Path

from core.config_loader import load_config, get_output_dir
from core.logger import setup_logger, get_logger

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
from modules.cloud import aws_enum, azure_enum, gcp_enum
from modules.web import url_collector, crawler, parameter_finder, js_parser
from modules.reporting import report_builder, html_report, markdown_report


def run(target: str, output_dir: str = None) -> str:
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
        target:     Target domain (e.g., example.com).
        output_dir: Optional existing output directory.

    Returns:
        Path to the generated HTML report.
    """
    config = load_config()
    if not output_dir:
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = get_output_dir(config, target, session_id)
    
    log_dir = config.get("log_dir", "logs")
    setup_logger(log_dir=log_dir, tool_name="recon_pipeline", target=target)
    log = get_logger(tool_name="recon_pipeline", target=target)

    log.info(f"=== RECON PIPELINE START | Target: {target} | Output: {output_dir} ===")

    # ── Stage 1: OSINT ───────────────────────────────────────────────────────
    log.info("[1/10] OSINT gathering")
    email_harvester.run(target, output_dir)
    metadata_scraper.run(target, output_dir)
    social_media_enum.run(target, output_dir)
    breach_lookup.run(target, output_dir)

    # ── Stage 2: Cloud Discovery ─────────────────────────────────────────────
    log.info("[2/10] Cloud discovery")
    aws_enum.run(target, output_dir)
    azure_enum.run(target, output_dir)
    gcp_enum.run(target, output_dir)

    # ── Stage 3: Subdomain Enumeration ──────────────────────────────────────
    log.info("[3/10] Subdomain enumeration")
    subdomain_enum.run(target, output_dir)

    # ── Stage 4: DNS Bruteforce ──────────────────────────────────────────────
    log.info("[4/10] DNS bruteforce")
    wordlist = config.get("wordlists", {}).get("dns", "")
    dns_bruteforce.run(target, output_dir, wordlist=wordlist if wordlist else None)

    # ── Stage 5: ASN / Reverse IP / WHOIS ───────────────────────────────────
    log.info("[5/10] ASN lookup")
    asn_lookup.run(target, output_dir)
    log.info("[5/10] Reverse IP lookup")
    reverse_ip.run(target, output_dir)
    log.info("[5/10] WHOIS lookup")
    whois_lookup.run(target, output_dir)

    # ── Stage 6: GitHub Dorking + S3 Buckets ────────────────────────────────
    log.info("[6/10] GitHub dorking")
    github_dorking.run(target, output_dir)
    log.info("[6/10] S3 bucket scan")
    s3_bucket_scan.run(target, output_dir)

    # ── Stage 7: URL Collection ──────────────────────────────────────────────
    log.info("[7/10] URL collection (gau + waybackurls)")
    url_collector.run(target, output_dir)

    # ── Stage 8: Web Crawl ───────────────────────────────────────────────────
    log.info("[8/10] Web crawl (katana)")
    target_url = f"https://{target}" if not target.startswith("http") else target
    crawler.run(target_url, output_dir)

    # ── Stage 9: JS Parsing + Parameter Discovery ────────────────────────────
    log.info("[9/10] JS file parsing")
    js_parser.run(target_url, output_dir)

    all_urls_file = f"{output_dir}/all_urls.txt"
    if Path(all_urls_file).exists():
        log.info("[9/10] Parameter discovery")
        parameter_finder.run(all_urls_file, output_dir)

    # ── Stage 10: Report ─────────────────────────────────────────────────────
    log.info("[10/10] Generating reports")
    results = report_builder.collect_results(output_dir)
    report_path = html_report.generate(results, output_dir)
    markdown_report.generate(results, output_dir)

    log.success(f"=== RECON PIPELINE COMPLETE | Report: {report_path} ===")
    return report_path
