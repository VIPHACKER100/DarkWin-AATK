# DARKWIN Changelog

All notable changes to DARKWIN are documented in this file.

---

## [1.1.0] — 2026-07-19

### Consolidated

- `core/tool_runner.py` — Shared `run_tool()` helper replacing 25 near-identical module wrappers. Each module now delegates the 3-step boilerplate (mkdir, log, run_command) to one function.
- Merged `modules/cloud/{aws,azure,gcp}_enum.py` → `cloud_enum.py` — three files calling the same tool with different `--disable-*` flags now call it once without flags (cloud_enum checks all providers by default).

### Removed

- `core/setup_wizard.py` — Interactive wizard replaced by "edit core/config.yaml directly."
- `modules/reporting/markdown_report.py` — Duplicated HTML report's data loop.
- `modules/cloud/utils.py` — 37-line filesystem search for one optional flag.
- `modules/vulnerabilities/*/__init__.py` (7 files) — Empty files, Python 3.3+ namespace packages don't need them.
- `docs/AI_MODULE_SPEC.md`, `docs/memory_map.md` — Speculative docs with no consuming code.
- `requirements.txt` — Dependencies duplicated in `pyproject.toml`.
- `core/engine.py` `_safe_command_for_log()` — Half-baked redaction; original cmd was still written verbatim to log file.
- `core/logger.py` `get_session_id()`, `get_log_file()` — Dead functions, imported nowhere.
- `core/config.yaml` `default_threads` — Key read by no code.
- `colorama` dependency — Rich handles colorized output natively.

### Fixed

- `core/engine.py` — Removed false-security redaction in command logging.
- `automation/full_scan_pipeline.py` — Removed unused `from core import engine`.
- All modules pass `py_compile` syntax verification (73 files).

---

## [1.0.0] — 2025-01-01

### Added — Core Engine

- `core/config_loader.py` — YAML config loader with `load_config()` and `get_output_dir()`
- `core/engine.py` — Shell command executor (`run_command`, `run_parallel`)
- `core/logger.py` — Structured loguru logging with session IDs and custom SUCCESS level
- `core/tool_loader.py` — Tool binary verifier with rich table output
- `core/pipeline.py` — Pipeline router (recon / scan / bounty modes)
- `core/darkwin.py` — Click CLI with `run`, `doctor`, `update` commands

### Added — Recon Modules

- `modules/recon/subdomain_enum.py` — subfinder + amass subdomain discovery
- `modules/recon/dns_bruteforce.py` — dnsrecon DNS brute-force
- `modules/recon/asn_lookup.py` — RADB whois ASN lookup
- `modules/recon/reverse_ip.py` — HackerTarget API + hakrevdns reverse IP lookup
- `modules/recon/whois_lookup.py` — whois domain registration data
- `modules/recon/github_dorking.py` — GitHub code search for sensitive leaks
- `modules/recon/s3_bucket_scan.py` — S3 bucket permutation scanner

### Added — OSINT Modules

- `modules/osint/email_harvester.py` — theHarvester email collection
- `modules/osint/metadata_scraper.py` — metagoofil document metadata
- `modules/osint/social_media_enum.py` — Sherlock username enumeration
- `modules/osint/breach_lookup.py` — HaveIBeenPwned API v3 integration

### Added — Web Discovery Modules

- `modules/web/crawler.py` — katana web crawler
- `modules/web/url_collector.py` — gau + waybackurls URL collection
- `modules/web/parameter_finder.py` — arjun parameter discovery
- `modules/web/js_parser.py` — subjs + linkfinder JS analysis

### Added — Vulnerability Modules

- `modules/vulnerabilities/xss/reflected_xss.py` — dalfox XSS scanner
- `modules/vulnerabilities/xss/dom_xss.py` — kxss DOM XSS detection
- `modules/vulnerabilities/sqli/sqli_detector.py` — sqlmap detection
- `modules/vulnerabilities/sqli/blind_sqli.py` — sqlmap time-based blind
- `modules/vulnerabilities/lfi/lfi_scanner.py` — ffuf LFI fuzzer
- `modules/vulnerabilities/ssrf/ssrf_tester.py` — ffuf SSRF tester
- `modules/vulnerabilities/rce/rce_scanner.py` — nuclei RCE templates
- `modules/vulnerabilities/csrf/csrf_detector.py` — nuclei CSRF templates

### Added — Fuzzing Modules

- `modules/fuzzing/directory_fuzzer.py` — ffuf directory fuzzer
- `modules/fuzzing/api_fuzzer.py` — ffuf API endpoint fuzzer
- `modules/fuzzing/parameter_fuzzer.py` — wfuzz parameter fuzzer

### Added — Network Modules

- `modules/network/port_scanner.py` — nmap full scan
- `modules/network/service_enum.py` — masscan fast discovery
- `modules/network/smb_enum.py` — enum4linux SMB enumeration
- `modules/network/ftp_enum.py` — nmap FTP scripts
- `modules/network/ssh_enum.py` — nmap SSH scripts

### Added — Cloud Modules

- `modules/cloud/cloud_enum.py` — cloud_enum multi-provider enumeration

### Added — Exploitation Modules

- `modules/exploitation/exploit_runner.py` — searchsploit with scope gate
- `modules/exploitation/metasploit_runner.py` — msfconsole resource file runner
- `modules/exploitation/payload_generator.py` — msfvenom payload generator

### Added — Reporting Modules

- `modules/reporting/report_builder.py` — output directory collector
- `modules/reporting/html_report.py` — Jinja2 HTML report generator

### Added — Automation Pipelines

- `automation/recon_pipeline.py` — full passive + active recon
- `automation/full_scan_pipeline.py` — comprehensive security scan
- `automation/bug_bounty_pipeline.py` — bug-bounty-optimised pipeline

### Added — Dashboard

- `dashboard/backend/app.py` — Flask + SocketIO REST API with live log streaming
- `dashboard/frontend/` — Next.js web frontend

### Added — Infrastructure

- `Dockerfile` — Kali Linux based container image
- `.github/workflows/ci.yml` — GitHub Actions CI (pytest on all pushes)
- `scripts/install_tools.sh` — One-command external tool installer
- `scripts/install_wordlists.sh` — SecLists + PayloadsAllTheThings installer
- `scripts/setup.sh` — Full setup orchestrator
- `templates/report.html.j2` — Jinja2 HTML report template
- `pyproject.toml` — PEP 517 build config with `darkwin` console script entry point
