# DARKWIN — Advanced Automation Toolkit

> ⚠️ **AUTHORIZED USE ONLY** — This toolkit is designed strictly for ethical security research, authorized penetration testing, and bug-bounty-scoped targets. Unauthorized use is illegal.

---

## Overview

DARKWIN is a modular, pipeline-driven automation toolkit for ethical hackers and bug bounty hunters. It chains together industry-standard security tools (subfinder, nuclei, dalfox, sqlmap, nmap, ffuf, and 15+ more) into smart, automated pipelines.

```
darkwin run recon  --target example.com
darkwin run scan   --target example.com
darkwin run bounty --target example.com
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
| Reporting      | HTML + Markdown auto-reports             |

---

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/VIPHACKER100/DarkWin-AATK
cd DarkWin-AATK
```

### 2. Run the setup script (installs all tools + wordlists)

```bash
bash scripts/setup.sh
```

### 3. Activate the virtual environment

```bash
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 4. Configure API keys

Edit `core/config.yaml`:

```yaml
api_keys:
  github_token: "YOUR_GITHUB_TOKEN"
  hibp_api_key: "YOUR_HIBP_KEY"
```

---

## Usage

```bash
# Full recon pipeline
darkwin run recon --target example.com

# Full vulnerability scan
darkwin run scan --target example.com

# Bug bounty optimized pipeline
darkwin run bounty --target example.com

# Verify all tools are installed
darkwin doctor

# Update DARKWIN and tools
darkwin update
```

---

## Architecture

```
DARKWIN/
├── core/           # Engine, CLI, config loader, logger
├── modules/        # Individual scan modules
│   ├── recon/      # 7 recon scripts
│   ├── osint/      # 4 OSINT scripts
│   ├── web/        # 4 web discovery scripts
│   ├── vulnerabilities/  # 9 vuln scripts
│   ├── fuzzing/    # 3 fuzzing scripts
│   ├── network/    # 5 network scripts
│   ├── cloud/      # 3 cloud scripts
│   ├── exploitation/     # 3 exploitation scripts
│   └── reporting/  # 3 reporting scripts
├── automation/     # Pipeline orchestrators
├── wordlists/      # SecLists + PayloadsAllTheThings
├── logs/           # Session logs
├── reports/        # Scan output
├── templates/      # HTML/MD report templates
└── scripts/        # Install & setup scripts
```

---

## Legal Disclaimer

This tool is provided for **educational and authorized security testing purposes only**. The authors are not responsible for any misuse. Always obtain explicit written authorization before testing any system.

---

## License

MIT License — © 2026 **ARYAN AHIRWAR (VIPHACKER.100)**
