# DarkWin-AATK: Comprehensive Technical Documentation & Architecture Reference

> **DarkWin - Automated Attack Toolkit (AATK)**  
> **Author:** Aryan Ahirwar (VIPHACKER.100)  
> **Repository:** `DarkWin-AATK`  
> **Specification Version:** 1.3.0 / CLI 1.2.0

---

## Table of Contents

1. [Executive Summary & System Architecture](#1-executive-summary--system-architecture)
2. [Project Layout & Directory Hierarchy](#2-project-layout--directory-hierarchy)
3. [Installation, Prerequisites & Deployment](#3-installation-prerequisites--deployment)
4. [CLI Usage & Command Reference](#4-cli-usage--command-reference)
5. [Core Framework Engine (`core/`)](#5-core-framework-engine-core)
   - [darkwin.py](#darkwinpy-cli-entrypoint)
   - [engine.py](#enginepy-orchestration-engine)
   - [pipeline.py](#pipelinepy-pipeline-dsl--executor)
   - [target.py](#targetpy-target-state--artifact-manager)
   - [tool_loader.py](#tool_loaderpy-external-binary-discovery)
   - [tool_runner.py](#tool_runnerpy-subprocess-execution--streaming)
   - [config_loader.py](#config_loaderpy-yaml-configuration-loader)
   - [progress.py & console_progress.py](#progresspy--console_progresspy-status-tracking)
   - [logger.py](#loggerpy-structured-logging)
6. [Automation Pipelines (`automation/`)](#6-automation-pipelines-automation)
   - [Recon Pipeline (`recon_pipeline.py`)](#recon-pipeline-recon_pipelinepy)
   - [Full Scan Pipeline (`full_scan_pipeline.py`)](#full-scan-pipeline-full_scan_pipelinepy)
   - [Bug Bounty Pipeline (`bug_bounty_pipeline.py`)](#bug-bounty-pipeline-bug_bounty_pipelinepy)
7. [Security Modules Reference (`modules/`)](#7-security-modules-reference-modules)
   - [Reconnaissance (`modules/recon/`)](#reconnaissance-modulesrecon)
   - [OSINT (`modules/osint/`)](#osint-modulesosint)
   - [Cloud Assessment (`modules/cloud/`)](#cloud-assessment-modulescloud)
   - [Web Discovery & Crawling (`modules/web/`)](#web-discovery--crawling-modulesweb)
   - [Network Scanning (`modules/network/`)](#network-scanning-modulesnetwork)
   - [Vulnerability Detection (`modules/vulnerabilities/`)](#vulnerability-detection-modulesvulnerabilities)
   - [Fuzzing (`modules/fuzzing/`)](#fuzzing-modulesfuzzing)
   - [Exploitation (`modules/exploitation/`)](#exploitation-modulesexploitation)
   - [Post-Exploitation (`modules/post_exploitation/`)](#post-exploitation-modulespost_exploitation)
   - [Reporting (`modules/reporting/`)](#reporting-modulesreporting)
8. [Dashboard Backend & Real-time Telemetry (`dashboard/backend/`)](#8-dashboard-backend--real-time-telemetry-dashboardbackend)
9. [Configuration Specification (`core/config.yaml`)](#9-configuration-specification-coreconfigyaml)
10. [Automation & Provisioning Scripts (`scripts/`)](#10-automation--provisioning-scripts-scripts)
11. [Testing Suite & Verification Strategy](#11-testing-suite--verification-strategy)
12. [External Tools & Binary Dependencies](#12-external-tools--binary-dependencies)
13. [Security, Ethics & Legal Disclaimer](#13-security-ethics--legal-disclaimer)

---

## 1. Executive Summary & System Architecture

**DarkWin-AATK** is an enterprise-grade automated penetration testing, vulnerability assessment, and reconnaissance framework written in Python. It bridges industry-standard offensive security tools (such as Nmap, Sublist3r, Amass, Katana, Nuclei, Sqlmap, Ffuf, Nikto, Metasploit, etc.) with custom Python logic into an asynchronous, pipeline-driven orchestration engine.

### High-Level Architecture

```
                    +--------------------------------+
                    |       DarkWin CLI / UI         |
                    | (Click CLI / Flask Dashboard)  |
                    +---------------+----------------+
                                    |
                                    v
                    +--------------------------------+
                    |      DarkWin Engine Core       |
                    |  - Target & Output Discovery   |
                    |  - Tool Runner (Async/Subproc) |
                    |  - YAML Configuration Loader   |
                    +---------------+----------------+
                                    |
                                    v
                    +--------------------------------+
                    |       Pipeline Executor        |
                    |  - Recon Pipeline              |
                    |  - Full Scan Pipeline          |
                    |  - Bug Bounty Pipeline         |
                    +---------------+----------------+
                                    |
        +---------------------------+---------------------------+
        |                           |                           |
        v                           v                           v
+----------------+          +----------------+          +----------------+
| Recon & OSINT  |          | Web & Network  |          | Exploitation & |
| - Subdomains   |          | - Port Scan    |          | Post-Exploit   |
| - DNS / ASN    |          | - Crawlers/JS  |          | - Payload Gen  |
| - Email/Breach |          | - Nuclei/XSS   |          | - Metasploit   |
| - Cloud S3     |          | - SQLi / SSRF  |          | - PrivEsc / Lin|
+----------------+          +----------------+          +----------------+
                                    |
                                    v
                    +--------------------------------+
                    |      Reporting Engine          |
                    | - Jinja2 HTML Report Generator |
                    | - JSON / Raw Evidence Archive  |
                    +--------------------------------+
```

### Key Architectural Tenets
- **Modular Plugin Pattern:** Every scanning phase is encapsulated in dedicated modules that interact through standard interfaces and artifact files.
- **Fail-Safe Subprocess Wrapping:** `ToolRunner` captures stdout, stderr, execution duration, and exit codes cleanly, ensuring a missing or failed third-party tool does not crash the entire scan chain.
- **Unified Target State:** The `Target` entity standardizes target parsing, creates isolated output trees per target, and manages intermediate artifacts.
- **Bi-directional Live Progress:** Emits structured progress updates via both console Rich tables/spinners and WebSockets (Flask-SocketIO).

---

## 2. Project Layout & Directory Hierarchy

```
DarkWin-AATK/
|-- pyproject.toml              # Project metadata, dependencies, entry points
|-- Dockerfile                  # Containerized deployment blueprint
|-- automation/                 # End-to-end multi-stage pipeline recipes
|   |-- __init__.py
|   |-- bug_bounty_pipeline.py  # Recon -> Parameters -> XSS/SQLi/SSRF/Nuclei
|   |-- full_scan_pipeline.py   # Comprehensive multi-vector scan & report
|   `-- recon_pipeline.py       # High-speed reconnaissance & asset enumeration
|-- core/                       # Foundational orchestration framework
|   |-- __init__.py
|   |-- config.yaml             # Master system defaults, tool flags, timeouts
|   |-- config_loader.py        # Configuration manager & YAML parser
|   |-- console_progress.py     # Rich terminal spinners, bars & status tables
|   |-- darkwin.py              # CLI entry point (`darkwin`)
|   |-- engine.py               # Engine coordinator for modules & pipelines
|   |-- logger.py               # Loguru-based structured logging
|   |-- pipeline.py             # Pipeline builder, task graph, & runner
|   |-- progress.py             # Abstract progress callbacks & socket events
|   |-- target.py               # Target normalization & directory management
|   |-- tool_loader.py          # Dynamic discovery of installed CLI utilities
|   `-- tool_runner.py          # Asynchronous / synchronous command execution
|-- dashboard/                  # Interactive management portal
|   `-- backend/
|       `-- app.py              # Flask + SocketIO REST & WebSocket server
|-- modules/                    # Offensive security capability libraries
|   |-- cloud/                  # Cloud security (S3, Azure, GCP buckets)
|   |-- exploitation/           # Exploit execution, Metasploit, payloads
|   |-- fuzzing/                # Directory, parameter, and API fuzzing
|   |-- network/                # Network discovery, port scanning, service checks
|   |-- osint/                  # Intelligence gathering, emails, breach data
|   |-- post_exploitation/      # Privilege escalation, persistence, lateral movement
|   |-- recon/                  # Subdomain enumeration, DNS brute, WHOIS, ASN
|   |-- reporting/              # HTML/PDF/JSON report compilation
|   |-- vulnerabilities/        # Focused vulnerability scanners (SQLi, XSS, SSRF...)
|   `-- web/                    # Web spiders, JS parsers, parameter extraction
|-- scripts/                    # Environment provisioning & setup scripts
|   |-- install_tools.sh        # Apt, Go, Python binary installer
|   |-- install_wordlists.sh    # SecLists & wordlist fetcher
|   `-- setup.sh                # Complete environment bootstrap
|-- templates/                  # Presentation templates
|   `-- report.html.j2          # Jinja2 template for executive HTML reports
`-- tests/                      # Pytest suite
    |-- integration/            # Multi-component and pipeline integration tests
    `-- unit/                   # Unit test coverage for modules and core classes
```

---

## 3. Installation, Prerequisites & Deployment

### Hardware & Platform Requirements
- **Operating System:** Linux (Debian, Ubuntu, Kali, ParrotOS recommended) or macOS / WSL2 on Windows.
- **Python Version:** Python >= 3.10
- **External Dependencies:** Go (>= 1.20), Git, Curl, Wget, Nmap, Masscan.

### Standard Setup

```bash
# 1. Clone repository
git clone https://github.com/VIPHACKER100/DarkWin-AATK.git
cd DarkWin-AATK

# 2. Run automated environment setup
chmod +x scripts/*.sh
./scripts/setup.sh

# 3. Manual Python installation (alternative)
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Docker Deployment

```bash
# Build the Docker container
docker build -t darkwin-aatk .

# Run DarkWin scan inside container with persistent volume
docker run --rm -v $(pwd)/results:/app/results darkwin-aatk scan --target example.com --pipeline recon
```

---

## 4. CLI Usage & Command Reference

The DarkWin-AATK Command-Line Interface is built using [Click](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/darkwin.py).

```bash
darkwin [OPTIONS] COMMAND [ARGS]...
```

### Global Options
- `--version` : Displays framework version.
- `--help` : Shows available commands and general help.

### Command Details

#### 1. `scan`
Executes an automated multi-stage pipeline against a specific target.
```bash
darkwin scan --target <DOMAIN_OR_IP> [OPTIONS]
```
- `-t, --target TEXT` *(Required)*: Target domain, IP address, or CIDR block (e.g. `example.com`, `192.168.1.1`).
- `-p, --pipeline [recon|full|bugbounty]` *(Default: `recon`)*: The automated orchestration pipeline to run.
- `-o, --output-dir PATH`: Directory where target artifacts and final reports will be saved (Default: `./results`).
- `-c, --config PATH`: Optional path to a custom YAML configuration file.
- `-v, --verbose`: Enables debug-level logging output.

#### 2. `run-module`
Executes an individual standalone module directly against a target.
```bash
darkwin run-module --target <TARGET> --module <MODULE_NAME> [OPTIONS]
```
- `-t, --target TEXT` *(Required)*: Target host or domain.
- `-m, --module TEXT` *(Required)*: Dot-notated module name (e.g., `recon.subdomain_enum`, `network.port_scanner`, `vulnerabilities.sqli_detector`).
- `-a, --args TEXT`: JSON-encoded key-value dictionary of module-specific parameters.
- `-o, --output-dir PATH`: Target output directory.

#### 3. `list-tools`
Audits the host environment and displays the installation status of all external CLI binaries utilized by DarkWin-AATK.
```bash
darkwin list-tools
```
Outputs a formatted table indicating:
- Tool Name
- System Path (`/usr/bin/...` or `Not Found`)
- Installation status flag (`[OK]` or `[MISSING]`)

#### 4. `dashboard`
Launches the Flask and Socket.IO real-time monitoring web dashboard.
```bash
darkwin dashboard [OPTIONS]
```
- `-h, --host TEXT` *(Default: `127.0.0.1`)*: Network interface binding.
- `-p, --port INTEGER` *(Default: `5000`)*: Port to serve dashboard traffic.

---

## 5. Core Framework Engine (`core/`)

### [darkwin.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/darkwin.py) (CLI Entrypoint)
- **Role:** Main command-line interface provider.
- **Key Functions:**
  - `cli()`: Base Click group declaring banner display and global flags.
  - `scan(target, pipeline, output_dir, config, verbose)`: Validates input, initialises the engine, creates target models, registers pipelines, and begins execution.
  - `run_module(target, module, args, output_dir)`: Loads a single isolated module and executes it with user-supplied JSON arguments.
  - `list_tools()`: Instantiates `ToolLoader` and outputs a color-coded status report of all required tools.
  - `dashboard(host, port)`: Launches the web management interface.

### [engine.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/engine.py) (Orchestration Engine)
- **Class:** `DarkWinEngine`
- **Role:** Coordinates targets, configurations, pipelines, and reporting.
- **Attributes:**
  - `config`: Loaded configuration dictionary.
  - `output_dir`: Root output directory path.
  - `logger`: Active structured logger.
  - `tool_loader`: Instance of `ToolLoader` for checking tool availability.
  - `pipelines`: Registry dictionary mapping pipeline names to execution functions.
- **Methods:**
  - `__init__(config_path=None, output_dir="results")`: Initializes engine, registers default pipelines (`recon`, `full`, `bugbounty`).
  - `register_pipeline(name: str, pipeline_func: Callable)`: Allows custom pipeline registration.
  - `run_pipeline(pipeline_name: str, target_str: str, progress_callback=None) -> Dict`: Main pipeline dispatcher. Initializes target directories, invokes the pipeline executor, aggregates artifacts, and outputs a summary.
  - `run_module(module_name: str, target: Target, **kwargs) -> Dict`: Dynamically imports and executes a single module's `run()` function.

### [pipeline.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/pipeline.py) (Pipeline DSL & Executor)
- **Classes:**
  - `PipelineStep`: Dataclass tracking individual tasks (name, function, arguments, status, execution duration, and error data).
  - `Pipeline`: Sequential execution container.
- **Key Methods (`Pipeline`):**
  - `add_step(name: str, func: Callable, *args, **kwargs)`: Appends a stage to the pipeline.
  - `execute(target: Target, progress_callback=None) -> Dict`: Sequentially runs each step, measures latency, records errors without terminating non-fatal stages, and calls `progress_callback` on state changes.

### [target.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/target.py) (Target State & Artifact Manager)
- **Class:** `Target`
- **Role:** Sanitizes and parses targets into hostnames, domains, IPs, or URLs; manages directory structure for target results.
- **Directory Structure Created per Target:**
  ```
  results/<target_sanitized>/
  |-- recon/
  |-- osint/
  |-- network/
  |-- web/
  |-- vulns/
  |-- fuzzing/
  |-- exploitation/
  |-- post_exploitation/
  |-- loot/
  `-- reports/
  ```
- **Key Methods & Properties:**
  - `raw`: The raw string target input.
  - `target_type`: Identified type (`domain`, `ip`, `cidr`, `url`).
  - `hostname`, `ip`, `port`, `url`: Normalised target attributes.
  - `get_output_dir(category: str) -> Path`: Returns the canonical directory for a given phase, creating it if necessary.
  - `get_artifact_path(category: str, filename: str) -> Path`: Returns the destination path for intermediate artifact files.

### [tool_loader.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/tool_loader.py) (External Binary Discovery)
- **Class:** `ToolLoader`
- **Role:** Checks system `$PATH` for the availability of security tools and binaries.
- **Attributes:**
  - `REQUIRED_TOOLS`: Exhaustive dictionary specifying binary names and functional categories.
- **Methods:**
  - `find_tool(tool_name: str) -> Optional[str]`: Uses `shutil.which` to discover binary locations on disk.
  - `check_all() -> Dict[str, Dict]`: Returns dictionary of all tools, their detected paths, and installed flags.
  - `get_missing() -> List[str]`: Returns a list of tools not currently present in the system environment.

### [tool_runner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/tool_runner.py) (Subprocess Execution & Streaming)
- **Class:** `ToolRunner`
- **Role:** Robust subprocess wrapper handling timeouts, real-time logging, output streaming, and error propagation.
- **Key Methods:**
  - `run(cmd: Union[str, List[str]], timeout: int = 300, cwd: str = None, env: dict = None) -> ToolResult`: Runs command synchronously, captures stdout and stderr, enforces timeouts, and returns a typed `ToolResult`.
  - `run_async(...)`: Asynchronous execution supporting non-blocking concurrent scans.
  - `run_piped(cmds: List[List[str]])`: Pipes stdout from one tool directly into the stdin of another (e.g. `subfinder | httpx`).

### [config_loader.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/config_loader.py) (YAML Configuration Loader)
- **Class:** `ConfigLoader`
- **Methods:**
  - `load_config(config_path: str = None) -> dict`: Reads `core/config.yaml` or a user-provided override, applies environment variable substitutions, and merges missing keys with defaults.
  - `get(key: str, default=None)`: Dot-delimited key retrieval (e.g. `config.get("tools.nmap.threads", 10)`).

### [progress.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/progress.py) & [console_progress.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/console_progress.py) (Status Tracking)
- **`ProgressCallback` Interface:** Base event listener class with methods `on_step_start(step_name)`, `on_step_complete(step_name, result)`, and `on_scan_complete(summary)`.
- **`ConsoleProgress`:** Concrete implementation utilizing `rich.progress` and `rich.table` to display interactive terminal UI with task progress, timing, and status icons.

### [logger.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/core/logger.py) (Structured Logging)
- **Role:** Configures Loguru logging across the application.
- **Features:** File rotation (10 MB per file), retention policies, standardized log formatting with thread/process IDs, and colorized console logging.

---

## 6. Automation Pipelines (`automation/`)

Pipelines chain multiple security modules into unified, multi-phase assessment workflows.

### Recon Pipeline (`recon_pipeline.py`)
Optimized for rapid asset discovery and attack surface mapping.
1. **Passive Subdomain Enumeration:** Runs Sublist3r, Assetfinder, Amass, and Subfinder to enumerate subdomains.
2. **DNS Resolution & Bruteforce:** Resolves discovered domains, finds active CNAMEs/A records via `puredns` or `massdns`.
3. **Reverse IP & ASN Lookup:** Resolves IP ranges, identifies hosting providers and neighbor hosts.
4. **WHOIS & Domain OSINT:** Queries domain registrar, creation dates, and administrative contacts.
5. **Port & Service Discovery:** Identifies open edge ports using Masscan and Nmap service probing.
6. **Web Probing & Live Asset Filtering:** Runs `httpx` to verify live web servers, status codes, and titles.

### Full Scan Pipeline (`full_scan_pipeline.py`)
Complete offensive security workflow spanning discovery to exploitation validation and report generation.
1. **Reconnaissance Stage:** Complete execution of the Recon Pipeline.
2. **OSINT Stage:** Harvests employee emails, leaked credentials, and metadata from documents.
3. **Web Crawling & Extraction:** Crawls all endpoints, parses JavaScript files, and extracts URL parameters.
4. **Vulnerability Assessment:** Executes automated checks for XSS, SQLi, LFI, SSRF, RCE, and IDOR vulnerabilities.
5. **Nuclei Automated Scanning:** Runs curated templates across all discovered live web applications.
6. **Network & Service Audit:** Tests SSH, FTP, and SMB services for default configurations and known CVEs.
7. **Report Compilation:** Compiles all findings, severity levels, and artifacts into an executive HTML and JSON report.

### Bug Bounty Pipeline (`bug_bounty_pipeline.py`)
Tailored specifically for bounty hunters seeking high-impact web vulnerabilities.
1. **Passive & Active Recon:** Fast subdomain gathering and live host identification.
2. **URL & Parameter Harvesting:** Extracts historical URLs from AlienVault OTX, Wayback Machine, and CommonCrawl; extracts inputs using `katana` and `gau`.
3. **High-Yield Web Vulnerability Scanners:**
   - Blind & Reflected XSS detection (`dalfox`).
   - SQL Injection identification (`sqlmap` & custom heuristics).
   - SSRF & Out-of-Band Callback Testing.
   - CORS, CSRF, and Open Redirect validation.
4. **Cloud Storage Exposure:** Scans for associated open AWS S3, GCP, and Azure Blob storage buckets.

---

## 7. Security Modules Reference (`modules/`)

### Reconnaissance (`modules/recon/`)

#### [subdomain_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/subdomain_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `sublist3r`, `subfinder`, `assetfinder`, `amass`
- **Description:** Aggregates passive and active subdomain enumeration results, removes duplicates, and saves resolved hosts to `recon/subdomains.txt`.

#### [dns_bruteforce.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/dns_bruteforce.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `puredns`, `massdns`, or native Python `aiodns`/`dnspython`
- **Description:** Brute-forces DNS records against a wordlist (e.g. `subdomains-top1mil.txt`) and discovers wildcard domains.

#### [reverse_ip.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/reverse_ip.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Queries HackerTarget and ViewDNS reverse IP APIs to discover co-hosted virtual hosts and domains sharing the target IP.

#### [whois_lookup.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/whois_lookup.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Performs WHOIS queries, extracts registrar details, registration/expiration timestamps, and nameservers.

#### [asn_lookup.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/asn_lookup.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Resolves IP address to Autonomous System Number (ASN), routing prefix, and ISP identification.

#### [github_dorking.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/github_dorking.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Searches GitHub via API or dorking patterns for leaked repository secrets, tokens, internal URLs, and configuration files matching the target domain.

#### [s3_bucket_scan.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/recon/s3_bucket_scan.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Generates permutation-based bucket names (e.g., `target-backup`, `target-assets`) and checks public AWS S3 bucket ACLs and permissions.

---

### OSINT (`modules/osint/`)

#### [email_harvester.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/osint/email_harvester.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `theHarvester`, Hunter.io API, search engine scraping
- **Description:** Extracts valid corporate email addresses, usernames, and employee names associated with the target domain.

#### [metadata_scraper.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/osint/metadata_scraper.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `exiftool`
- **Description:** Downloads public documents (`.pdf`, `.docx`, `.xlsx`, `.pptx`) from the target web assets and extracts author names, internal printer names, software versions, and internal folder paths.

#### [social_media_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/osint/social_media_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Enumerates brand accounts and corporate presences across LinkedIn, Twitter/X, GitHub, and Facebook.

#### [breach_lookup.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/osint/breach_lookup.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Cross-references harvested emails against known public data breaches and credential dumps using HaveIBeenPwned or dehashed-style endpoints.

---

### Cloud Assessment (`modules/cloud/`)

#### [cloud_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/cloud/cloud_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Multi-cloud enumeration module auditing exposed assets across Amazon Web Services (S3, CloudFront), Google Cloud Platform (GCS Storage), and Microsoft Azure (Blob Containers).

---

### Web Discovery & Crawling (`modules/web/`)

#### [url_collector.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/web/url_collector.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `waybackurls`, `gau`, `alienvault`
- **Description:** Queries historical passive web archives to assemble an inventory of historical URLs, query parameters, and forgotten endpoints.

#### [crawler.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/web/crawler.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `katana`, `gospider`
- **Description:** Crawls web applications, handles forms, maintains session cookies, and discovers dynamic client-side routes.

#### [js_parser.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/web/js_parser.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** Regex engine, JS beautifier
- **Description:** Analyzes JavaScript bundles and source maps to uncover hardcoded API keys, JWTs, hidden endpoints, and staging server URLs.

#### [parameter_finder.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/web/parameter_finder.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `arjun`, `paramminer`
- **Description:** Discovers hidden GET and POST parameters on endpoints vulnerable to parameter pollution or injection.

---

### Network Scanning (`modules/network/`)

#### [port_scanner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/network/port_scanner.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `nmap`, `masscan`
- **Description:** Conducts high-speed SYN port scans, identifying accessible TCP/UDP ports and mapping perimeter infrastructure.

#### [service_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/network/service_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `nmap -sV -sC`
- **Description:** Performs banner grabbing, service protocol interrogation, and runs NSE service discovery scripts.

#### [smb_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/network/smb_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `enum4linux`, `smbclient`
- **Description:** Audits SMB/SAMBA shares (ports 139/445), checks for anonymous guest access, enumerates users, and audits IPC shares.

#### [ftp_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/network/ftp_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Verifies anonymous login access on port 21, crawls available directories, and checks for vulnerable FTP server versions.

#### [ssh_enum.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/network/ssh_enum.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Analyzes SSH key exchange algorithms, ciphers, and checks against weak credential pairs.

---

### Vulnerability Detection (`modules/vulnerabilities/`)

#### [reflected_xss.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/xss/reflected_xss.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `dalfox` or custom payload reflector
- **Description:** Injects context-aware XSS probes across URL parameters, evaluating HTML reflection, character filtering, and script execution contexts.

#### [dom_xss.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/xss/dom_xss.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Parses client-side scripts to map unsafe sinks (`innerHTML`, `document.write`, `eval`) receiving untrusted inputs from sources (`location.search`, `location.hash`).

#### [sqli_detector.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/sqli/sqli_detector.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `sqlmap` or error-based heuristic generator
- **Description:** Tests database error signatures (MySQL, MSSQL, Oracle, Postgres, SQLite) triggered by arithmetic mutations and quote injections.

#### [blind_sqli.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/sqli/blind_sqli.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Uses time-delay payloads (e.g. `pg_sleep`, `WAITFOR DELAY`, `sleep()`) to detect blind SQL injection vulnerabilities.

#### [lfi_scanner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/lfi/lfi_scanner.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Tests path traversal strings (`../../../../etc/passwd`, `..\..\..\windows\win.ini`), null-byte wrappers, and PHP filter streams (`php://filter/convert.base64-encode/resource=...`).

#### [ssrf_tester.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/ssrf/ssrf_tester.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Injects loopback indicators (`127.0.0.1`, `[::]`, `169.254.169.254`) and Out-Of-Band callback identifiers into URL-type parameters.

#### [rce_scanner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/rce/rce_scanner.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Detects OS command injection via shell command chaining operators (`;`, `|`, `&&`, `` ` ``), validating output via command execution echoes or sleep delays.

#### [csrf_detector.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/csrf/csrf_detector.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Audits web application forms for missing anti-CSRF tokens, SameSite cookie configurations, and permissive CORS headers.

#### [idor_scanner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/vulnerabilities/idor/idor_scanner.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Tests authorization boundaries by incrementing or decrementing numeric object IDs, testing access control enforcement across user contexts.

---

### Fuzzing (`modules/fuzzing/`)

#### [directory_fuzzer.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/fuzzing/directory_fuzzer.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `ffuf`, `gobuster`, `dirb`
- **Description:** Fuzzes target web paths against SecLists wordlists to find hidden administrative portals, backup files (`.bak`, `.old`), and exposed `.git` directories.

#### [api_fuzzer.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/fuzzing/api_fuzzer.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Tests REST, GraphQL, and SOAP API routes using HTTP verb tampering (`PUT`, `DELETE`, `PATCH`), invalid JSON payloads, and parameter fuzzing.

#### [parameter_fuzzer.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/fuzzing/parameter_fuzzer.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `ffuf`
- **Description:** Discovers hidden request parameters via high-concurrency fuzzing, monitoring HTTP response body size and status code changes.

---

### Exploitation (`modules/exploitation/`)

#### [exploit_runner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/exploitation/exploit_runner.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `searchsploit`
- **Description:** Queries Exploit-DB for known exploits matching discovered software versions and automates Proof-of-Concept verification.

#### [metasploit_runner.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/exploitation/metasploit_runner.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `msfconsole`, `pymetasploit3` (RPC API)
- **Description:** Connects to Metasploit RPC daemon, configures module payloads (`LHOST`, `RHOSTS`), and verifies exploitable vulnerabilities.

#### [payload_generator.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/exploitation/payload_generator.py)
- **Function:** `generate(payload_type: str, lhost: str, lport: int, format: str = "raw") -> str`
- **Tools Utilized:** `msfvenom`
- **Description:** Programmatically generates reverse shells, web shells, and staged/stageless payloads across multiple formats (`elf`, `exe`, `php`, `asp`, `war`).

---

### Post-Exploitation (`modules/post_exploitation/`)

#### [privesc_checker.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/post_exploitation/privesc_checker.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** LinPEAS / WinPEAS
- **Description:** Analyzes compromised hosts for privilege escalation vectors, including SUID binaries, misconfigured sudoers, unquoted service paths, and kernel vulnerabilities.

#### [lateral_movement.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/post_exploitation/lateral_movement.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Tools Utilized:** `impacket` (`psexec.py`, `wmiexec.py`)
- **Description:** Validates discovered credentials across network segments, testing pass-the-hash, WMI, and WinRM access.

#### [persistence_auditor.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/post_exploitation/persistence_auditor.py)
- **Function:** `run(target: Target, config: dict) -> dict`
- **Description:** Audits compromised systems for unauthorized persistence mechanisms, including cron jobs, systemd services, SSH authorized keys, and scheduled tasks.

---

### Reporting (`modules/reporting/`)

#### [report_builder.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/reporting/report_builder.py)
- **Class:** `ReportBuilder`
- **Methods:**
  - `add_finding(title, severity, description, evidence, recommendation)`
  - `build_summary() -> dict`: Aggregates vulnerabilities by severity (Critical, High, Medium, Low, Informational).
  - `export_json(filepath: Path)`: Exports full finding data as structured JSON.

#### [html_report.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/modules/reporting/html_report.py)
- **Function:** `generate_html_report(target: Target, scan_data: dict, output_file: Path)`
- **Template:** `templates/report.html.j2`
- **Description:** Renders a responsive HTML executive report featuring vulnerability distributions, severity scorecards, step-by-step evidence, and remediation advice.

---

## 8. Dashboard Backend & Real-time Telemetry (`dashboard/backend/`)

### [app.py](file:///c:/Users/vipha/Desktop/DarkWin-AATK/dashboard/backend/app.py)
The web interface is powered by Flask and Flask-SocketIO.

#### REST Endpoints
| HTTP Method | Route | Description |
|---|---|---|
| `GET` | `/` | Web dashboard root and status verification |
| `GET` | `/api/status` | System health, engine version, and active scan status |
| `GET` | `/api/tools` | Status and paths of all registered external tools |
| `GET` | `/api/scans` | List of all historical scans and completed targets |
| `GET` | `/api/scans/<target>` | Detailed scan report and findings for a given target |
| `POST`| `/api/scans/start` | Trigger a new pipeline scan (`{target, pipeline, config}`) |
| `POST`| `/api/scans/stop` | Terminate an active scanning process |

#### WebSocket Events (Socket.IO)
- `connect`: Emitted upon client connection; sends system status.
- `disconnect`: Handles client disconnection.
- `scan_progress`: Streams live scan progress updates (`step`, `percentage`, `status`, `message`).
- `tool_output`: Streams raw stdout/stderr output lines from active CLI tools.

---

## 9. Configuration Specification (`core/config.yaml`)

```yaml
# DarkWin-AATK Master Configuration
version: "1.3.0"

general:
  output_dir: "results"
  threads: 10
  timeout: 300
  user_agent: "Mozilla/5.0 (DarkWin-AATK Security Scanner)"

logging:
  level: "INFO"
  format: "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
  rotation: "10 MB"
  retention: "14 days"

tools:
  nmap:
    threads: 10
    default_ports: "top-1000"
    timing: "-T4"
  masscan:
    rate: 1000
  subfinder:
    timeout: 30
  httpx:
    threads: 50
    follow_redirects: true
  nuclei:
    severity: "critical,high,medium"
    concurrency: 25
  ffuf:
    threads: 40
    extensions: ".php,.html,.js,.txt,.json,.bak"

wordlists:
  subdomains: "/usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt"
  directories: "/usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt"
  parameters: "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt"
```

---

## 10. Automation & Provisioning Scripts (`scripts/`)

### [scripts/setup.sh](file:///c:/Users/vipha/Desktop/DarkWin-AATK/scripts/setup.sh)
- Master bootstrap script:
  1. Checks for root privileges.
  2. Updates package manager repositories (`apt update`).
  3. Installs core dependencies (`python3-pip`, `golang`, `git`, `curl`).
  4. Calls `install_tools.sh` and `install_wordlists.sh`.
  5. Sets up the Python virtual environment and installs package requirements.

### [scripts/install_tools.sh](file:///c:/Users/vipha/Desktop/DarkWin-AATK/scripts/install_tools.sh)
- Installs external CLI security tools:
  - **Apt Packages:** `nmap`, `masscan`, `smbclient`, `enum4linux`, `exiftool`, `nikto`
  - **Go Binaries:** `subfinder`, `httpx`, `nuclei`, `katana`, `ffuf`, `gau`, `assetfinder`
  - **Python Utilities:** `sqlmap`, `theHarvester`, `arjun`, `dalfox`

### [scripts/install_wordlists.sh](file:///c:/Users/vipha/Desktop/DarkWin-AATK/scripts/install_wordlists.sh)
- Fetches wordlists for fuzzing and discovery:
  - Clones [SecLists](https://github.com/danielmiessler/SecLists) to `/usr/share/seclists`.
  - Downloads Assetnote wordlists for API and parameter fuzzing.

---

## 11. Testing Suite & Verification Strategy

The test suite covers both unit testing of individual modules and integration testing of end-to-end pipelines.

```bash
# Run the complete test suite
pytest -v

# Run only unit tests
pytest tests/unit/ -v

# Run integration tests
pytest tests/integration/ -v
```

### Test Organization
- **`tests/unit/` (26 test files):**
  - Core testing: `test_engine.py`, `test_target.py`, `test_tool_runner.py`, `test_tool_loader.py`, `test_pipeline.py`.
  - Module testing: Dedicated unit tests with mocked subprocess outputs for all recon, web, OSINT, network, fuzzing, vulnerability, and exploitation modules.
- **`tests/integration/` (7 test files):**
  - End-to-end pipeline execution tests (`test_recon_pipeline.py`, `test_full_scan.py`).
  - Reporting integration and Dashboard WebSocket API tests.

---

## 12. External Tools & Binary Dependencies

| Category | Tool | Binary / Package | Primary Use Case |
|---|---|---|---|
| **Recon** | Subfinder | `subfinder` | Fast passive subdomain discovery |
| **Recon** | Assetfinder | `assetfinder` | Passive domain enumeration via public sources |
| **Recon** | Amass | `amass` | In-depth network mapping and DNS enumeration |
| **Recon** | PureDNS | `puredns` | High-speed wildcard-filtering DNS resolution |
| **Network**| Nmap | `nmap` | Port scanning, OS detection, service enumeration |
| **Network**| Masscan | `masscan` | High-speed asynchronous port scanning |
| **Web** | HTTPX | `httpx` | Live web server probing and title extraction |
| **Web** | Katana | `katana` | Web crawling and spidering |
| **Web** | GAU | `gau` | URL harvesting from public web archives |
| **Fuzzing**| FFUF | `ffuf` | Directory and parameter fuzzing |
| **Vuln** | Nuclei | `nuclei` | Fast, template-based vulnerability scanning |
| **Vuln** | SQLMap | `sqlmap` | Automated SQL injection testing |
| **Vuln** | Dalfox | `dalfox` | Parameter analysis and XSS scanner |
| **OSINT** | theHarvester | `theHarvester` | Email and subdomain OSINT gathering |
| **Exploit**| Metasploit | `msfconsole` | Exploit execution and payload delivery |

---

## 13. Security, Ethics & Legal Disclaimer

> **IMPORTANT:**  
> **DarkWin-AATK** is designed strictly for authorized penetration testing, security assessments, and academic research. 
> 
> Testing targets without prior mutual, written consent is illegal in most jurisdictions. Users are solely responsible for adhering to applicable local, state, and international cyber laws. The authors and contributors assume no liability for misuse or damage caused by this software.
