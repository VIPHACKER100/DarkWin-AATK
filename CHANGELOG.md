# DARKWIN Changelog

All notable changes to DARKWIN are documented in this file.

---

## [1.2.0] — 2026-07-19

### Dashboard — Design System Overhaul

- Applied full design system: Calistoga (display), Inter (UI), JetBrains Mono (labels)
- Gradient accent `#0052FF → #4D7CFF` on CTAs, icons, progress bars, featured cards
- Reusable components: Button (primary/secondary/ghost/danger), Card (standard/elevated/featured gradient border), Input with focus ring
- Animated entrance transitions (StaggerContainer, AnimatedSection, SectionLabel badge)
- Floating y-axis animations on progress icon and empty-state icon
- Inverted contrast section for scan progress (light foreground + dot pattern)
- Centralized CSS custom properties and shadow tokens (`--shadow-accent`, `--shadow-accent-lg`)
- `prefers-reduced-motion` media query
- Global `*:focus-visible` ring

### Dashboard — New Functionality

- **Scan initiation from UI** — target input, mode selector (recon/scan/bounty), launch button
- **Real-time scan progress** — animated gradient bar with pipeline-accurate phase names
- **Tool status panel** — collapsible sidebar with per-tool pass/fail, refresh button
- **Socket connection indicator** — Online/Reconnecting/Offline with colored pulse dot
- **Target search/filter** — live filter input in sidebar
- **Toast notifications** — success/error/info with slide-in animation and auto-dismiss
- **Delete targets and sessions** — trash buttons with confirmation modal
- **Auto-scroll toggle** — Eye icon to pause/resume log terminal auto-scroll
- **Keyboard shortcuts** — Enter to launch scan, Escape to clear logs
- **Scan history dropdown** — past 10 scans with mode/status/timestamps
- **Loading skeletons** — pulsing placeholders while data loads
- **Configurable via env vars** — `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_SOCKET_URL`

### Dashboard — Backend

- `POST /scan` — start a pipeline scan in a background thread
- `GET /tools` — return tool verification status as JSON
- `GET /scan/current` — poll current running scan state
- `GET /scan/history` — last 20 scans
- `DELETE /target/<target>` — delete all sessions for a target
- `DELETE /target/<target>/<session>` — delete a single session
- SocketIO events: `scan_phase`, `scan_done`, `scan_error`, `target_deleted`, `session_deleted`
- Env var config: `DARKWIN_PORT`, `DARKWIN_REPORTS_DIR`, `DARKWIN_LOGS_DIR`, `DARKWIN_CORS_ORIGIN`
- Structured error responses: `{"error": "...", "code": ...}`
- GET /targets now returns session metadata (hasReport, modified timestamp)

### Bug Fixes (Kali Testing)

- `config.yaml`: httpx → curl (Python httpx package shadowed ProjectDiscovery httpx)
- `email_harvester.py`: added `-q` flag for quieter theHarvester output
- `url_collector.py`: gau uses `--o` not `-o`, waybackurls reads from stdin pipe
- `js_parser.py`: prepend `https://` for subjs, linkfinder `-i URL -o cli`, replaced fragile cat|xargs|curl|grep pipeline with direct Python curl + re search
- `dns_bruteforce.py`: fixed `-t brt -D` flag order
- `port_scanner.py`: `-p-` timeout → `--top-ports 1000 -T4`
- `directory_fuzzer.py`, `api_fuzzer.py`: `-silent` → `-s`
- `parameter_fuzzer.py`: added `2>&1` stderr redirect
- `subdomain_enum.py`: added `-timeout 2` to amass
- `parameter_finder.py`: arjun `-oT` → `-o json -f json`
- `whois_lookup.py`, `asn_lookup.py`: added `2>&1` stderr redirect
- `smb_enum.py` (enum4linux), `service_enum.py` (masscan): added `2>&1` stderr redirect
- `test_network_modules.py`: new test file for port_scanner

### Installer

- `scripts/install_tools.sh`: complete rewrite with `--only`, `--missing` flags, 3-attempt retry with GOPROXY fallback, per-tool failure reporting, `setup_go_env()` with `go env -w`, `chown` back to SUDO_USER, `--break-system-packages` flag
- Always symlinks Go binaries to `/usr/local/bin/` regardless of "already installed" state

### CLI & Documentation

- Detailed help text on all CLI commands (`run`/`doctor`/`update`/`dashboard`) with pipeline descriptions and usage examples
- `-h` shorthand for help in addition to `--help`

### CI & Build

- Added `[test]` optional dependencies (`pytest`, `pytest-cov`) to `pyproject.toml`
- CI workflow now installs `.[test]` instead of bare package
- Fixed TypeScript build error: `GradientText` `children` type changed from `string` to `React.ReactNode`

---

## [1.1.0] — 2026-07-19

### Consolidated

- `core/tool_runner.py` — Shared `run_tool()` helper replacing 25 near-identical module wrappers
- Merged `modules/cloud/{aws,azure,gcp}_enum.py` → `cloud_enum.py`

### Removed

- `core/setup_wizard.py`, `modules/reporting/markdown_report.py`, `modules/cloud/utils.py`
- 7 empty `__init__.py` files, `docs/AI_MODULE_SPEC.md`, `docs/memory_map.md`, `requirements.txt`
- Dead functions: `_safe_command_for_log()`, `get_session_id()`, `get_log_file()`
- Unused config key `default_threads`
- `colorama` dependency (Rich handles colorized output natively)

### Fixed

- Removed false-security redaction in command logging
- Removed unused import in `full_scan_pipeline.py`
- `setup.sh` no longer references `requirements.txt`
- README CLI usage examples corrected
- `install_tools.sh`: GOPATH preservation under sudo, `shutil.which` instead of bash `which`

---

## [1.0.0] — 2025-01-01

### Added — Core Engine

- `core/config_loader.py` — YAML config loader
- `core/engine.py` — Shell command executor (`run_command`, `run_parallel`)
- `core/logger.py` — Structured loguru logging with session IDs
- `core/tool_loader.py` — Tool binary verifier with rich table output
- `core/pipeline.py` — Pipeline router (recon / scan / bounty)
- `core/darkwin.py` — Click CLI with `run`, `doctor`, `update` commands

### Added — Modules

- Recon: subdomain_enum, dns_bruteforce, asn_lookup, reverse_ip, whois_lookup, github_dorking, s3_bucket_scan
- OSINT: email_harvester, metadata_scraper, social_media_enum, breach_lookup
- Web: crawler, url_collector, parameter_finder, js_parser
- Vulnerabilities: XSS (reflected + DOM), SQLi (detector + blind), LFI, SSRF, RCE, CSRF
- Fuzzing: directory_fuzzer, api_fuzzer, parameter_fuzzer
- Network: port_scanner, service_enum, smb_enum, ftp_enum, ssh_enum
- Cloud: cloud_enum
- Exploitation: exploit_runner, metasploit_runner, payload_generator
- Reporting: report_builder, html_report

### Added — Dashboard

- `dashboard/backend/app.py` — Flask + SocketIO REST API
- `dashboard/frontend/` — Next.js web frontend

### Added — Infrastructure

- Dockerfile, GitHub Actions CI, scripts/install_tools.sh, scripts/install_wordlists.sh, scripts/setup.sh
- `templates/report.html.j2` — Jinja2 HTML report template
- `pyproject.toml` — PEP 517 build config with `darkwin` console script entry point
