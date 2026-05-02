# DARKWIN Changelog — [bold cyan]By ARYAN AHIRWAR [VIPHACKER.100](/bold cyan)

All notable changes to DARKWIN are documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.0] — 2025-01-01

### Added — Core Engine

- `core/config_loader.py` — YAML config loader with `load_config()` and `get_output_dir()`
- `core/engine.py` — Shell command executor (`run_command`, `run_parallel`)
- `core/logger.py` — Structured loguru logging with session IDs and custom SUCCESS level
- `core/tool_loader.py` — Tool binary verifier with rich table output
- `core/pipeline.py` — Pipeline router (recon / scan / bounty modes)
- `core/darkwin.py` — Click CLI with `run`, `doctor`, `update` commands

### Added — Recon Modules (7 scripts)

- `modules/recon/subdomain_enum.py` — subfinder + amass subdomain discovery
- `modules/recon/dns_bruteforce.py` — dnsrecon DNS brute-force
- `modules/recon/asn_lookup.py` — RADB whois ASN lookup
- `modules/recon/reverse_ip.py` — HackerTarget API + hakrevdns reverse IP lookup
- `modules/recon/whois_lookup.py` — whois domain registration data
- `modules/recon/github_dorking.py` — GitHub code search for sensitive leaks
- `modules/recon/s3_bucket_scan.py` — S3 bucket permutation scanner

### Added — OSINT Modules (4 scripts)

- `modules/osint/email_harvester.py` — theHarvester email collection
- `modules/osint/metadata_scraper.py` — metagoofil document metadata
- `modules/osint/social_media_enum.py` — Sherlock username enumeration
- `modules/osint/breach_lookup.py` — HaveIBeenPwned API v3 integration

### Added — Web Discovery Modules (4 scripts)

- `modules/web/crawler.py` — katana web crawler
- `modules/web/url_collector.py` — gau + waybackurls URL collection
- `modules/web/parameter_finder.py` — arjun parameter discovery
- `modules/web/js_parser.py` — subjs + linkfinder JS analysis

### Added — Vulnerability Modules (9 scripts)

- `modules/vulnerabilities/xss/reflected_xss.py` — dalfox XSS scanner
- `modules/vulnerabilities/xss/dom_xss.py` — kxss DOM XSS detection
- `modules/vulnerabilities/sqli/sqli_detector.py` — sqlmap detection
- `modules/vulnerabilities/sqli/blind_sqli.py` — sqlmap time-based blind
- `modules/vulnerabilities/lfi/lfi_scanner.py` — ffuf LFI fuzzer
- `modules/vulnerabilities/ssrf/ssrf_tester.py` — ffuf SSRF tester
- `modules/vulnerabilities/rce/rce_scanner.py` — nuclei RCE templates
- `modules/vulnerabilities/csrf/csrf_detector.py` — nuclei CSRF templates

### Added — Fuzzing Modules (3 scripts)

- `modules/fuzzing/directory_fuzzer.py` — ffuf directory fuzzer
- `modules/fuzzing/api_fuzzer.py` — ffuf API endpoint fuzzer
- `modules/fuzzing/parameter_fuzzer.py` — wfuzz parameter fuzzer

### Added — Network Modules (5 scripts)

- `modules/network/port_scanner.py` — nmap full scan
- `modules/network/service_enum.py` — masscan fast discovery
- `modules/network/smb_enum.py` — enum4linux SMB enumeration
- `modules/network/ftp_enum.py` — nmap FTP scripts
- `modules/network/ssh_enum.py` — nmap SSH scripts

### Added — Cloud Modules (3 scripts)

- `modules/cloud/aws_enum.py` — cloud_enum AWS
- `modules/cloud/azure_enum.py` — cloud_enum Azure
- `modules/cloud/gcp_enum.py` — cloud_enum GCP

### Added — Exploitation Modules (3 scripts)

- `modules/exploitation/exploit_runner.py` — searchsploit with scope gate
- `modules/exploitation/metasploit_runner.py` — msfconsole resource file runner
- `modules/exploitation/payload_generator.py` — msfvenom payload generator

### Added — Reporting Modules (3 scripts)

- `modules/reporting/report_builder.py` — output directory collector
- `modules/reporting/html_report.py` — Jinja2 HTML report generator
- `modules/reporting/markdown_report.py` — Markdown report generator

### Added — Automation Pipelines (3 pipelines)

- `automation/recon_pipeline.py` — full passive + active recon
- `automation/full_scan_pipeline.py` — comprehensive security scan
- `automation/bug_bounty_pipeline.py` — bug-bounty-optimised pipeline

### Added — Dashboard (Phase 16)

- `dashboard/backend/app.py` — Flask + SocketIO REST API with live log streaming

### Added — Infrastructure

- `Dockerfile` — Kali Linux based container image
- `.github/workflows/ci.yml` — GitHub Actions CI (pytest on all pushes)
- `scripts/install_tools.sh` — One-command external tool installer
- `scripts/install_wordlists.sh` — SecLists + PayloadsAllTheThings installer
- `scripts/setup.sh` — Full setup orchestrator
- `templates/report.html.j2` — Jinja2 HTML report template
- `pyproject.toml` — PEP 517 build config with `darkwin` console script entry point

---

## [1.1.0] — 2026-05-02

### Added

- `darkwin setup` — New interactive configuration wizard to set up API keys and directories.
- `darkwin doctor --fix` — Added automated dependency installation for missing tools on Linux/WSL.
- `core/setup_wizard.py` — Implementation of the interactive setup logic.
- Parallel Execution — Refactored `recon_pipeline.py` to run OSINT, Cloud Discovery, and Lookups concurrently using `ThreadPoolExecutor`.
- **DARKWIN Control Center** — New Next.js web dashboard with real-time log streaming via Socket.IO.
- `dashboard/frontend` — Full Next.js frontend implementation with a hacker-themed HUD.
- `darkwin dashboard` — CLI command to launch the web interface.

### Fixed

- `core/logger.py` — Fixed `ValueError` when registering the `SUCCESS` log level multiple times.
- `cloud_enum` path issue — Fixed "Cannot access mutations file" error by auto-detecting the wordlist path.
- Improved error handling in the execution engine for better CLI feedback.

---

## [Planned] — Phase 2 AI Features

See `docs/AI_MODULE_SPEC.md` for the planned AI module specification.
