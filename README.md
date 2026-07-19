# DARKWIN — Advanced Automation Toolkit

> ⚠️ **AUTHORIZED USE ONLY** — This toolkit is designed strictly for ethical security research, authorized penetration testing, and bug-bounty-scoped targets. Unauthorized use is illegal.

---

## Overview

DARKWIN is a modular, pipeline-driven automation toolkit for ethical hackers and bug bounty hunters. It chains together industry-standard security tools (subfinder, nuclei, dalfox, sqlmap, nmap, ffuf, and 15+ more) into smart, automated pipelines.

```
darkwin run --mode recon  --target example.com
darkwin run --mode scan   --target example.com
darkwin run --mode bounty --target example.com
```

---

## Features

| Category       | Tools Integrated                         |
|----------------|------------------------------------------|
| Recon          | subfinder, amass, dnsrecon, whois, gau   |
| OSINT          | theHarvester, sherlock, metagoofil       |
| Web Discovery  | katana, gau, waybackurls, arjun          |
| Vulnerability  | dalfox, sqlmap, nuclei, ffuf, kxss       |
| Fuzzing        | ffuf, wfuzz                              |
| Network        | nmap, masscan, enum4linux                |
| Cloud          | cloud_enum                               |
| Tool Runner    | Shared run_tool() helper — 25 modules → 1 pattern |
| Reporting      | HTML auto-reports                        |
| Concurrency    | Parallel stage execution (ThreadPool)     |
| Dashboard      | Real-time web UI (Next.js + Socket.IO)    |

---

## Setup

### 1. Clone and enter the repository

```bash
git clone https://github.com/VIPHACKER100/DarkWin-AATK
cd DarkWin-AATK
```

### 2. Run the setup script (creates venv, installs deps, tools, wordlists)

```bash
bash scripts/setup.sh
```

### 3. Activate the virtual environment

```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 4. Configure API keys

Edit `core/config.yaml` to configure API keys and paths.

---

## Usage

```bash
# Full recon pipeline
darkwin run --mode recon --target example.com

# Full vulnerability scan
darkwin run --mode scan --target example.com

# Bug bounty optimized pipeline
darkwin run --mode bounty --target example.com

# Verify all tools are installed
darkwin doctor

# Automatically fix missing dependencies (Linux/WSL)
darkwin doctor --fix

# Update DARKWIN and tools
darkwin update

# Launch the Web Dashboard
darkwin dashboard
```

---

## ⚡ Advanced Commands

| Command | Description |
|---------|-------------|
| `darkwin doctor` | Verify all required tools are installed. |
| `darkwin doctor --fix` | Automatically install missing Go/Python/apt dependencies. |
| `darkwin dashboard` | Start the Flask backend and Next.js frontend Control Center. |
| `darkwin run --mode bounty --target site.com --confirm-scope` | Run bounty mode with automatic authorization confirmation. |
| `darkwin run --mode recon --target site.com --dashboard` | Run a scan and stream live logs to the dashboard. |

---

## 🖥️ Web Dashboard (Control Center)

DARKWIN v1.1.0 includes a modern Next.js dashboard for real-time monitoring.

1. **Start the backend**: `darkwin dashboard`
2. **Start the frontend**: `cd dashboard/frontend && npm run dev`
3. **Access**: [http://localhost:3000](http://localhost:3000)

---

## Architecture

```
DARKWIN/
├── core/           # Engine, CLI, config loader, logger, shared tool_runner
├── modules/        # Individual scan modules
│   ├── recon/      # 7 recon scripts
│   ├── osint/      # 4 OSINT scripts
│   ├── web/        # 4 web discovery scripts
│   ├── vulnerabilities/  # 9 vuln scripts
│   ├── fuzzing/    # 3 fuzzing scripts
│   ├── network/    # 5 network scripts
│   ├── cloud/      # Cloud enumeration
│   ├── exploitation/     # 3 exploitation scripts
│   └── reporting/  # HTML report generator
├── automation/     # Pipeline orchestrators
├── wordlists/      # SecLists + PayloadsAllTheThings
├── logs/           # Session logs
├── reports/        # Scan output
├── templates/      # HTML report template
└── scripts/        # Install & setup scripts
```

---

## Legal Disclaimer

This tool is provided for **educational and authorized security testing purposes only**. The authors are not responsible for any misuse. Always obtain explicit written authorization before testing any system.

---

## License

MIT License — © 2026 **ARYAN AHIRWAR (VIPHACKER.100)**
