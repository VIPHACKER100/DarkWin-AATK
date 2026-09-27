# DARKWIN — Advanced Automated Attack Toolkit (AATK)

> ⚠️ **AUTHORIZED USE ONLY** — Designed exclusively for authorized penetration testing, security assessments, ethical research, and scoped bug bounty programs. Unauthorized access or scanning without prior written consent is illegal.

<p align="center">
  <img src="https://img.shields.io/badge/version-1.3.0-blueviolet" alt="Version 1.3.0">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/docker-ready-2496ED" alt="Docker Ready">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/author-ARYAN%20AHIRWAR-orange" alt="Author ARYAN AHIRWAR">
</p>

---

## 📖 Table of Contents
- [Overview](#-overview)
- [Quick Start](#-quick-start)
- [Documentation Suite](#-documentation-suite)
- [Architecture & Pipelines](#-architecture--pipelines)
- [Security Capabilities & Modules](#-security-capabilities--modules)
- [CLI Reference](#-cli-reference)
- [Web Dashboard](#-web-dashboard)
- [Docker Deployment](#-docker-deployment)
- [Testing Suite](#-testing-suite)
- [Directory Layout](#-directory-layout)
- [Legal Disclaimer & License](#-legal-disclaimer--license)

---

## ⚡ Overview

**DARKWIN (AATK)** is an enterprise-grade automated penetration testing and reconnaissance orchestration framework. It seamlessly integrates **30+ industry-standard offensive security tools** (Nmap, Subfinder, Amass, Katana, Nuclei, Sqlmap, Ffuf, Dalfox, Metasploit, etc.) into unified, asynchronous, multi-stage attack pipelines with rich console telemetry, interactive HTML reporting, and an integrated real-time Web Dashboard.

```bash
# Reconnaissance & Perimeter Mapping
darkwin scan --target example.com --pipeline recon

# Full-Spectrum Vulnerability Assessment
darkwin scan --target example.com --pipeline full

# Bug Bounty Hunting Workflow
darkwin scan --target example.com --pipeline bugbounty
```

---

## 🚀 Quick Start

### 1. Automated Installation (Linux / Kali / Parrot / WSL2)

```bash
git clone https://github.com/VIPHACKER100/DarkWin-AATK.git
cd DarkWin-AATK

# Run automated bootstrap (installs dependencies, Go binaries, SecLists, & creates venv)
chmod +x scripts/*.sh
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Verify installed external tools
darkwin list-tools
```

### 2. Manual Installation

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -e .
darkwin list-tools
```

---

## 📚 Documentation Suite

Full technical guides, architectural blueprints, module specifications, and developer playbooks are available in the [`DOCS/`](DOCS/README.md) directory:

| Guide | Description |
|---|---|
| 📑 [DOCS/README.md](DOCS/README.md) | **Documentation Index**: Quick navigation and directory overview |
| 📖 [DOCS/DOCUMENTATION.md](DOCS/DOCUMENTATION.md) | **Master Technical Specification**: Comprehensive documentation of every function, feature, engine component, CLI command, configuration, and testing strategy |
| 💻 [DOCS/CLI_GUIDE.md](DOCS/CLI_GUIDE.md) | **CLI Operator Playbook**: Command syntax, parameter tables, real-world pentesting workflows, and troubleshooting |
| 🏛️ [DOCS/ARCHITECTURE.md](DOCS/ARCHITECTURE.md) | **System Architecture & Design**: Concurrency model, lifecycle of a scan, target state machine, subprocess isolation, and telemetry protocol |
| 📦 [DOCS/MODULES_CATALOG.md](DOCS/MODULES_CATALOG.md) | **Security Modules Catalog**: Detailed reference for all 50+ modules across all 10 categories, including external tools, commands, and generated artifacts |
| 🛠️ [DOCS/DEVELOPER_GUIDE.md](DOCS/DEVELOPER_GUIDE.md) | **Developer & Contributor Guide**: Instructions for creating custom security modules, writing custom automation pipelines, using `ToolRunner`, and writing tests with mock fixtures |

---

## 🔄 Architecture & Pipelines

DARKWIN provides three purpose-built scanning pipelines:

| Pipeline | Key Stages | Best For |
|---|---|---|
| **`recon`** | Subdomain Enum → DNS Resolution → Reverse IP → WHOIS/ASN → Port Scan → Web Probing | Passive & active perimeter mapping, attack surface discovery |
| **`full`** | Recon → OSINT → Web Crawling → Vuln Assessment (XSS, SQLi, LFI, SSRF, RCE) → Nuclei → Network Audit → HTML Report | Comprehensive penetration testing & compliance audits |
| **`bugbounty`** | Fast Recon → Archive URL Mining → Parameter Discovery → High-Impact Vulns (XSS/SQLi/SSRF) → S3 & Cloud Exposure | Bug bounty hunting and high-signal vulnerability identification |

---

## 🛡️ Security Capabilities & Modules

DARKWIN includes over **50 modular capabilities** organized across 10 functional domains:

| Category | Modules | External Binaries & Libraries |
|---|---|---|
| **Reconnaissance** | Subdomain discovery, DNS brute, Reverse IP, WHOIS, ASN lookup, GitHub dorking, S3 bucket enumeration | `subfinder`, `assetfinder`, `amass`, `puredns`, `massdns` |
| **OSINT** | Email harvesting, document metadata extraction, social media enumeration, credential breach lookups | `theHarvester`, `exiftool`, Hunter.io, HIBP APIs |
| **Cloud Security** | Cloud storage & asset enumeration across AWS, GCP, and Azure | `cloud_enum`, AWS S3 API |
| **Web Discovery** | Archive URL harvesting, deep crawling, JavaScript static analysis, hidden parameter extraction | `katana`, `gau`, `waybackurls`, `arjun`, `gospider` |
| **Network & Services** | Port scanning, service versioning, SMB auditing, anonymous FTP checks, SSH cipher analysis | `nmap`, `masscan`, `smbclient`, `enum4linux` |
| **Vulnerabilities** | Reflected & DOM XSS, Error & Blind SQLi, LFI/Path Traversal, SSRF, RCE, CSRF, IDOR | `nuclei`, `dalfox`, `sqlmap`, custom heuristic engines |
| **Fuzzing** | High-speed directory fuzzing, REST/GraphQL API fuzzing, query parameter fuzzing | `ffuf`, `gobuster` |
| **Exploitation** | Exploit-DB matching, Metasploit RPC execution, multi-format payload generation | `searchsploit`, `pymetasploit3`, `msfconsole`, `msfvenom` |
| **Post-Exploitation**| Privilege escalation auditing, credential testing, persistence checks | LinPEAS, WinPEAS, Impacket |
| **Reporting** | Severity aggregation, finding correlation, executive Jinja2 HTML and structured JSON generation | `Jinja2`, `rich`, `ReportBuilder` |

---

## 💻 CLI Reference

### 1. `scan` — Execute Automated Pipeline
```bash
darkwin scan --target <DOMAIN_OR_IP> [OPTIONS]
```
- `-t, --target TEXT` *(Required)*: Target domain, IP address, or URL.
- `-p, --pipeline [recon|full|bugbounty]` *(Default: `recon`)*: Pipeline to execute.
- `-o, --output-dir PATH` *(Default: `./results`)*: Output directory for scan artifacts.
- `-c, --config PATH`: Optional path to custom YAML config.
- `-v, --verbose`: Enable debug logging.

### 2. `run-module` — Execute Single Module
```bash
darkwin run-module --target <TARGET> --module <MODULE_NAME> [OPTIONS]
```
- `-t, --target TEXT` *(Required)*: Target host or domain.
- `-m, --module TEXT` *(Required)*: Dot-notated module name (e.g. `recon.subdomain_enum`, `network.port_scanner`).
- `-a, --args TEXT`: JSON dictionary of module-specific parameters.
- `-o, --output-dir PATH`: Target output directory.

### 3. `list-tools` — Environment Audit
```bash
darkwin list-tools
```
Scans system `$PATH` and displays a color-coded status table indicating whether required external binaries are installed.

### 4. `dashboard` — Launch Web Management Console
```bash
darkwin dashboard --host 127.0.0.1 --port 5000
```
Launches the Flask & Socket.IO real-time telemetry server.

---

## 🖥️ Web Dashboard

DARKWIN features a real-time web portal powered by Flask and Socket.IO:

- **Launch Backend:**
  ```bash
  darkwin dashboard --host 127.0.0.1 --port 5000
  ```
- **Optional Frontend Dev Server (Next.js):**
  ```bash
  cd dashboard/frontend && npm run dev
  ```

### Dashboard Features:
- **Scan Management:** Launch, pause, or abort pipeline scans from the UI.
- **Live Terminal Telemetry:** Real-time stdout/stderr stream from background tools via WebSockets.
- **Interactive Report Viewer:** Embedded HTML reports with severity metrics and vulnerability breakdown.
- **Tool Health Monitor:** Live status indicators for all registered external security binaries.

---

## 🐳 Docker Deployment

Run DARKWIN in an isolated container with all tools pre-configured:

```bash
# Build the Docker image
docker build -t darkwin-aatk .

# Run a scan with results saved to your host machine
docker run --rm -v $(pwd)/results:/app/results darkwin-aatk scan --target example.com --pipeline recon
```

---

## 🧪 Testing Suite

DARKWIN includes an extensive Pytest suite covering both unit and integration tests:

```bash
# Run all tests
pytest -v

# Run unit tests only
pytest tests/unit/ -v

# Run integration tests only
pytest tests/integration/ -v
```

---

## 📁 Directory Layout

```
DarkWin-AATK/
|-- pyproject.toml              # Project metadata, dependencies, CLI entrypoint
|-- Dockerfile                  # Containerized deployment specification
|-- README.md                   # Project overview & quick start
|-- DOCS/                       # Comprehensive documentation suite
|   |-- README.md               # Documentation suite index
|   |-- DOCUMENTATION.md        # Master technical reference
|   |-- CLI_GUIDE.md            # Operator playbook & workflow guide
|   |-- ARCHITECTURE.md         # System design & lifecycle specifications
|   |-- MODULES_CATALOG.md      # 50+ module reference catalog
|   `-- DEVELOPER_GUIDE.md      # Plugin & pipeline developer guide
|-- automation/                 # Pipeline orchestration logic
|   |-- recon_pipeline.py       # High-speed recon pipeline
|   |-- full_scan_pipeline.py   # Comprehensive multi-vector scan pipeline
|   `-- bug_bounty_pipeline.py  # Bug-bounty-optimized pipeline
|-- core/                       # Foundational orchestration framework
|   |-- darkwin.py              # Click CLI entrypoint
|   |-- engine.py               # DarkWinEngine controller
|   |-- pipeline.py             # Pipeline task runner & DSL
|   |-- target.py               # Target normalization & artifact tree manager
|   |-- tool_runner.py          # Subprocess wrapper with timeout & streaming
|   |-- tool_loader.py          # Binary discovery across $PATH
|   |-- config_loader.py        # YAML configuration loader
|   |-- progress.py             # Event listener interfaces
|   |-- console_progress.py     # Rich terminal spinners and tables
|   |-- logger.py               # Loguru structured logging
|   `-- config.yaml             # System defaults, timeouts, wordlists
|-- dashboard/                  # Management portal
|   |-- backend/app.py          # Flask + Socket.IO REST & WebSocket API
|   `-- frontend/               # Next.js web application
|-- modules/                    # Offensive capability libraries (50+ modules)
|   |-- recon/                  # Subdomains, DNS, WHOIS, ASN, GitHub, S3
|   |-- osint/                  # Emails, metadata, social media, breaches
|   |-- cloud/                  # AWS, Azure, GCP storage audits
|   |-- web/                    # Crawling, JS parsing, parameter discovery
|   |-- network/                # Port scanning, service versioning, SMB, FTP, SSH
|   |-- vulnerabilities/        # XSS, SQLi, LFI, SSRF, RCE, CSRF, IDOR
|   |-- fuzzing/                # Directory, API, and parameter fuzzing
|   |-- exploitation/           # Exploit-DB, Metasploit RPC, payload gen
|   |-- post_exploitation/      # LinPEAS/WinPEAS, lateral movement, persistence
|   `-- reporting/              # ReportBuilder and Jinja2 HTML generator
|-- templates/                  # Jinja2 HTML report templates
|-- scripts/                    # Bootstrap and installation shell scripts
`-- tests/                      # Pytest unit and integration test suite
```

---

## ⚖️ Legal Disclaimer & License

### Disclaimer
This software is provided for **educational and authorized security testing purposes only**. Scanning or attempting to compromise targets without prior explicit written authorization from the target owner is strictly illegal under local, federal, and international law. The developers and contributors assume no liability for misuse, damages, or legal consequences resulting from the use of this toolkit.

### License
Released under the **MIT License**.  
Copyright © 2026 **ARYAN AHIRWAR (VIPHACKER.100)**. All rights reserved.
