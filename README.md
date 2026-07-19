# DARKWIN — Advanced Automation Toolkit

> ⚠️ **AUTHORIZED USE ONLY** — Designed for ethical security research, authorized penetration testing, and bug-bounty–scoped targets. Unauthorized use is illegal.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/next.js-16.2-blueviolet" alt="Next.js 16">
</p>

---

## Overview

DARKWIN chains 30+ industry-standard security tools (subfinder, nuclei, dalfox, nmap, ffuf, and more) into three smart pipelines — recon, scan, and bounty — wrapped in a modern real-time dashboard.

```
darkwin run --mode recon  --target example.com
darkwin run --mode scan   --target example.com
darkwin run --mode bounty --target example.com
```

---

## Quick Start

```bash
git clone https://github.com/VIPHACKER100/DarkWin-AATK
cd DarkWin-AATK
bash scripts/setup.sh          # creates venv, installs deps + tools
source venv/bin/activate
darkwin doctor                  # verify all 30+ tools
```

Configure API keys in `core/config.yaml`.

---

## Features

| Area | Tools |
|------|-------|
| **Recon** | subfinder, amass, dnsrecon, whois, gau, katana |
| **OSINT** | theHarvester, sherlock, metagoofil |
| **Web Discovery** | katana, gau, waybackurls, arjun, subjs, linkfinder |
| **Vulnerability** | dalfox, sqlmap, nuclei, kxss |
| **Fuzzing** | ffuf, wfuzz |
| **Network** | nmap, masscan, enum4linux |
| **Cloud** | cloud_enum |
| **Exploitation** | searchsploit, msfconsole, msfvenom |
| **Dashboard** | Real-time web UI (Next.js + Socket.IO + Flask) |
| **Tool Runner** | Shared `run_tool()` — one pattern for all 25+ modules |
| **Reporting** | Auto-generated HTML reports |
| **Concurrency** | Parallel stage execution via ThreadPool |

---

## Usage

```bash
darkwin run --mode recon --target example.com
darkwin run --mode scan --target example.com
darkwin run --mode bounty --target example.com --confirm-scope
darkwin doctor                          # verify tools
darkwin doctor --fix                    # auto-install missing tools
darkwin update                          # git pull + re-verify
darkwin dashboard                       # launch backend + frontend
```

### Advanced

| Command | Description |
|---------|-------------|
| `darkwin run --dashboard` | Run a scan with live logs streamed to the dashboard |
| `darkwin doctor --fix` | Auto-install missing Go/Python/apt dependencies |
| `sudo bash scripts/install_tools.sh` | Install all external tools |
| `sudo bash scripts/install_tools.sh --only subfinder,gau` | Install specific tools only |
| `sudo bash scripts/install_tools.sh --missing` | Auto-detect and install only what's missing |
| `cd dashboard/frontend && npm run dev` | Start frontend dev server on `:3000` |

---

## 🖥️ Web Dashboard

DARKWIN includes a full-featured real-time dashboard built with Next.js 16 and Flask + Socket.IO.

**Start it:**
```bash
darkwin dashboard           # backend on :5000
cd dashboard/frontend && npm run dev   # frontend on :3000
```

**Features:**
- **Scan initiation** — type a target, pick a mode (recon/scan/bounty), launch from the UI
- **Real-time progress** — live phase tracking with animated gradient progress bar
- **Live log streaming** — Socket.IO–powered terminal with auto-scroll toggle and line numbers
- **Report viewer** — embedded iframe for HTML scan reports
- **Tool status panel** — collapsible sidebar showing all 30+ tools ✓/✗
- **Target management** — search/filter, delete targets and sessions from the UI
- **Toast notifications** — scan completed, failed, and deletion confirmations
- **Socket status indicator** — Online/Reconnecting/Offline with visual pulse

**Frontend design system:**
- Fonts: Calistoga (display), Inter (UI), JetBrains Mono (labels)
- Gradient accent: `#0052FF → #4D7CFF` on CTAs, icons, progress bars
- Animated entrance transitions (Framer Motion)
- Dark theme with dot-pattern textures and radial glows

---

## Pipeline Modes

| Mode | Phases | Use Case |
|------|--------|----------|
| `recon` | Subdomains → HTTPX → URL collection → Crawl → Nuclei | Passive + active reconnaissance |
| `scan` | Recon → Port scan → Web scan → XSS → Nuclei | Full vulnerability assessment |
| `bounty` | Recon → Port scan → Web scan → XSS → Nuclei → Gowitness | Bug-bounty–optimised with screenshots |

---

## Architecture

```
DARKWIN/
├── core/              # Engine, CLI, config, logger, tool_runner
├── modules/
│   ├── recon/         # 7 recon scripts
│   ├── osint/         # 4 OSINT scripts
│   ├── web/           # 5 web discovery scripts
│   ├── vulnerabilities/  # 9 vuln scripts
│   ├── fuzzing/       # 3 fuzzing scripts
│   ├── network/       # 5 network scripts
│   ├── cloud/         # Cloud enumeration
│   ├── exploitation/  # 3 exploitation scripts
│   └── reporting/     # HTML report generator
├── automation/        # Pipeline orchestrators (recon/scan/bounty)
├── dashboard/
│   ├── backend/       # Flask REST API + Socket.IO
│   └── frontend/      # Next.js app (App Router)
│       ├── app/       # Pages, layout, globals.css
│       ├── components/# Reusable UI (Button, Card, Input, SectionLabel)
│       └── lib/       # API client, Socket.IO client, utilities
├── wordlists/         # SecLists + PayloadsAllTheThings
├── scripts/           # install_tools.sh, install_wordlists.sh, setup.sh
├── logs/              # Session logs
├── reports/           # Scan output
├── templates/         # Jinja2 HTML report template
└── tests/             # Unit + integration tests
```

---

## Legal Disclaimer

This tool is provided for **educational and authorized security testing purposes only**. The authors are not responsible for any misuse. Always obtain explicit written authorization before testing any system.

---

## License

MIT License — © 2026 **ARYAN AHIRWAR (VIPHACKER.100)**
