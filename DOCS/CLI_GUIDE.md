# DarkWin-AATK CLI User Guide & Operational Playbook

> Comprehensive operator handbook for the **DarkWin - Automated Attack Toolkit (AATK)** command-line interface.

---

## Table of Contents
1. [Overview & Binary Setup](#1-overview--binary-setup)
2. [Global Command Structure](#2-global-command-structure)
3. [Command: `scan`](#3-command-scan)
4. [Command: `run-module`](#4-command-run-module)
5. [Command: `list-tools`](#5-command-list-tools)
6. [Command: `dashboard`](#6-command-dashboard)
7. [Real-World Pentest Workflows](#7-real-world-pentest-workflows)
   - [Workflow A: External Web Penetration Test](#workflow-a-external-web-penetration-test)
   - [Workflow B: Bug Bounty Recon & Surface Discovery](#workflow-b-bug-bounty-recon--surface-discovery)
   - [Workflow C: Internal Network & Service Audit](#workflow-c-internal-network--service-audit)
8. [Managing Artifacts & Outputs](#8-managing-artifacts--outputs)
9. [Troubleshooting & Diagnostics](#9-troubleshooting--diagnostics)

---

## 1. Overview & Binary Setup

DarkWin CLI (`darkwin`) is the primary interface for running security scans, driving automated pipelines, inspecting tool availability, and managing target output.

Once installed in your Python environment via `pip install -e .` or poetry/flit, the `darkwin` command is accessible globally.

Verify your environment before scanning:

```bash
# Verify CLI entrypoint
darkwin --help

# Verify installed external binaries
darkwin list-tools
```

---

## 2. Global Command Structure

```
darkwin [OPTIONS] COMMAND [ARGS]...
```

### Global Flags
- `--help`: Show the interactive help message and exit.
- `--version`: Print framework release version.

### Available Subcommands
- `scan`: Execute an automated multi-stage scanning pipeline against a target.
- `run-module`: Execute a single standalone module with custom parameters.
- `list-tools`: Check availability and paths of third-party command-line binaries.
- `dashboard`: Launch the real-time Flask + Socket.IO web telemetry portal.

---

## 3. Command: `scan`

The `scan` command is the main engine entry point. It takes a target, initializes the per-target workspace directory, sets up logging, and executes the selected pipeline stages.

### Syntax
```bash
darkwin scan --target <TARGET> [OPTIONS]
```

### Parameter Reference

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--target` | `-t` | String | *Required* | Domain, IP address, CIDR, or URL to assess. |
| `--pipeline` | `-p` | Choice (`recon`, `full`, `bugbounty`) | `recon` | Automated pipeline sequence to run. |
| `--output-dir` | `-o` | Path | `./results` | Root folder to store all scan results and artifacts. |
| `--config` | `-c` | Path | None | Path to custom YAML configuration file. |
| `--verbose` | `-v` | Flag | `False` | Enable debug-level log output to console. |

### Usage Examples

#### Run Fast Passive & Active Recon
```bash
darkwin scan --target example.com --pipeline recon
```

#### Run Bug Bounty Hunting Pipeline
```bash
darkwin scan --target target.com --pipeline bugbounty -o /data/pentest-results
```

#### Run Comprehensive Assessment with Debug Logs
```bash
darkwin scan --target 192.168.1.100 --pipeline full -v -c ./custom_config.yaml
```

---

## 4. Command: `run-module`

Execute an individual standalone module directly without running a multi-stage pipeline.

### Syntax
```bash
darkwin run-module --target <TARGET> --module <MODULE_NAME> [OPTIONS]
```

### Parameter Reference

| Flag | Short | Type | Default | Description |
|---|---|---|---|---|
| `--target` | `-t` | String | *Required* | Target host, domain, or IP. |
| `--module` | `-m` | String | *Required* | Module path in dot notation (e.g. `recon.subdomain_enum`). |
| `--args` | `-a` | JSON String | `{}` | JSON dictionary of keyword arguments passed to `run()`. |
| `--output-dir` | `-o` | Path | `./results` | Target artifact directory. |

### Usage Examples

#### Run Subdomain Enumeration Only
```bash
darkwin run-module \
  --target example.com \
  --module recon.subdomain_enum
```

#### Run Port Scanner with Custom Ports
```bash
darkwin run-module \
  --target 10.10.10.50 \
  --module network.port_scanner \
  --args '{"ports": "21,22,80,443,445,8080", "scan_type": "syn"}'
```

#### Run Directory Fuzzer with a Specific Wordlist
```bash
darkwin run-module \
  --target https://app.example.com \
  --module fuzzing.directory_fuzzer \
  --args '{"wordlist": "/usr/share/seclists/Discovery/Web-Content/common.txt", "threads": 50}'
```

#### Run SQL Injection Detector
```bash
darkwin run-module \
  --target "https://shop.example.com/item?id=1" \
  --module vulnerabilities.sqli_detector \
  --args '{"level": 3, "risk": 2}'
```

---

## 5. Command: `list-tools`

Scans your system environment `$PATH` and verifies whether required external security binaries are installed and accessible.

### Syntax
```bash
darkwin list-tools
```

### Example Output
```
+---------------+------------------------+----------+
| Tool Name     | System Path            | Status   |
+---------------+------------------------+----------+
| nmap          | /usr/bin/nmap          | [OK]     |
| masscan       | /usr/bin/masscan       | [OK]     |
| subfinder     | /root/go/bin/subfinder | [OK]     |
| httpx         | /root/go/bin/httpx     | [OK]     |
| nuclei        | /root/go/bin/nuclei    | [OK]     |
| katana        | /root/go/bin/katana    | [OK]     |
| ffuf          | /root/go/bin/ffuf      | [OK]     |
| sqlmap        | /usr/bin/sqlmap        | [OK]     |
| dalfox        | /root/go/bin/dalfox    | [OK]     |
| theHarvester  | /usr/local/bin/theHarv | [OK]     |
| msfconsole    | Not Found              | [MISSING]|
+---------------+------------------------+----------+
[!] 1 tool(s) missing. Run ./scripts/install_tools.sh to install missing binaries.
```

---

## 6. Command: `dashboard`

Launches the web-based graphical management console and real-time execution monitor.

### Syntax
```bash
darkwin dashboard [OPTIONS]
```

### Parameter Reference

| Flag | Short | Default | Description |
|---|---|---|---|
| `--host` | `-h` | `127.0.0.1` | Network interface to bind the Flask web application. |
| `--port` | `-p` | `5000` | Port number to expose the web server on. |

### Usage
```bash
# Bind to localhost
darkwin dashboard

# Bind to all interfaces for remote monitoring
darkwin dashboard --host 0.0.0.0 --port 8080
```
Then navigate to `http://localhost:5000` in your web browser.

---

## 7. Real-World Pentest Workflows

### Workflow A: External Web Penetration Test
When assigned an external web application penetration test:

```bash
# Step 1: Check dependencies
darkwin list-tools

# Step 2: Run passive & active surface discovery
darkwin scan --target clientapp.com --pipeline recon -o ./engagement_clientapp

# Step 3: Run full vulnerability & misconfiguration audit
darkwin scan --target clientapp.com --pipeline full -o ./engagement_clientapp -v

# Step 4: Examine generated executive report
open ./engagement_clientapp/clientapp.com/reports/report.html
```

### Workflow B: Bug Bounty Recon & Surface Discovery
Targeting large-scope wildcard domains (e.g. `*.examplecorp.com`):

```bash
# Step 1: Run Bug Bounty Pipeline
darkwin scan --target examplecorp.com --pipeline bugbounty -o ./bounties

# Step 2: Target specific high-value endpoints discovered by katana/gau
darkwin run-module \
  --target "https://auth.examplecorp.com/login" \
  --module vulnerabilities.reflected_xss

darkwin run-module \
  --target "https://api.examplecorp.com/v1/users" \
  --module vulnerabilities.idor_scanner
```

### Workflow C: Internal Network & Service Audit
Auditing an internal IP address or subnet:

```bash
# Step 1: Scan top ports and services
darkwin run-module \
  --target 10.0.0.15 \
  --module network.port_scanner

# Step 2: Audit SMB and Windows shares
darkwin run-module \
  --target 10.0.0.15 \
  --module network.smb_enum

# Step 3: Run post-exploitation LinPEAS audit on target shell
darkwin run-module \
  --target 10.0.0.15 \
  --module post_exploitation.privesc_checker
```

---

## 8. Managing Artifacts & Outputs

All results are automatically categorized under your designated output directory (`./results` by default):

```
results/example.com/
|-- recon/
|   |-- subdomains.txt      # Clean deduplicated list of discovered subdomains
|   |-- dns_records.json    # Resolved DNS A, AAAA, CNAME, MX records
|   |-- whois.json          # Registrar and administrative records
|   `-- live_hosts.txt      # Hosts answering HTTP/HTTPS probes
|-- web/
|   |-- urls.txt            # Crawled & historical endpoints
|   |-- parameters.json     # Extracted GET/POST parameter names
|   `-- js_endpoints.txt    # URLs and tokens extracted from JS scripts
|-- network/
|   |-- open_ports.txt      # Open ports per host
|   `-- services.xml        # Detailed Nmap service version data
|-- vulns/
|   |-- nuclei_findings.json# Nuclei template matches
|   |-- xss_results.json    # XSS reflections and PoC links
|   `-- sqli_findings.json  # Injected parameters and DB types
`-- reports/
    |-- report.html         # Formatted interactive HTML executive report
    `-- findings.json       # Machine-readable vulnerability summary
```

---

## 9. Troubleshooting & Diagnostics

### Missing External Tools
If a tool reports `[MISSING]` during `darkwin list-tools`:
```bash
# Ensure Go binaries directory is in your PATH
export PATH=$PATH:$HOME/go/bin:/usr/local/go/bin

# Re-run the automated tool installation script
bash scripts/install_tools.sh
```

### Permission Denied on Raw Socket Scans (Nmap / Masscan)
Masscan and SYN port scans (`-sS`) require root or `CAP_NET_RAW` privileges:
```bash
sudo $(which darkwin) scan --target example.com --pipeline recon
# OR grant capabilities to python/nmap:
sudo setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip $(which nmap)
```

### Subprocess Timeouts
For large scopes where tools like `amass` or `nuclei` exceed default limits, adjust timeout values in `core/config.yaml` or provide a custom config:
```yaml
general:
  timeout: 1200 # increase timeout to 20 minutes
```
```bash
darkwin scan --target bigscope.com --config ./custom_timeout.yaml
```
