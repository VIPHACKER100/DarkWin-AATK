#!/usr/bin/env bash
# DARKWIN — Tool Installer
# Installs all required external tools for the DARKWIN toolkit.
# Run as root or with sudo on Kali Linux / Debian-based systems.

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERR]${NC}   $*"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        warn "Not running as root. Some installs may fail."
        warn "Re-run with: sudo bash scripts/install_tools.sh"
    fi
}

install_go_tool() {
    local name="$1"
    local pkg="$2"
    if which "$name" &>/dev/null; then
        success "$name already installed"
    else
        info "Installing $name via go install..."
        go install "$pkg" 2>/dev/null && success "$name installed" || error "Failed to install $name"
    fi
}

install_apt() {
    local pkg="$1"
    local binary="${2:-$1}"
    if which "$binary" &>/dev/null; then
        success "$binary already installed"
    else
        info "Installing $pkg via apt..."
        apt-get install -y "$pkg" &>/dev/null && success "$pkg installed" || error "Failed to install $pkg"
    fi
}

install_pip() {
    local pkg="$1"
    local binary="${2:-$1}"
    if which "$binary" &>/dev/null; then
        success "$binary already installed"
    else
        info "Installing $pkg via pip3..."
        pip3 install "$pkg" &>/dev/null && success "$pkg installed" || error "Failed to install $pkg"
    fi
}

# ── Prerequisites ────────────────────────────────────────────────────────────
check_root
info "Updating apt package index..."
apt-get update -qq

# ── Go (required for most tools) ─────────────────────────────────────────────
if ! which go &>/dev/null; then
    info "Installing Go..."
    apt-get install -y golang-go &>/dev/null
fi
export GOPATH="$HOME/go"
export PATH="$PATH:$GOPATH/bin"

# ── apt-based tools ───────────────────────────────────────────────────────────
info "=== Installing apt-based tools ==="
install_apt nmap
install_apt masscan
install_apt sqlmap
install_apt whois
install_apt dnsrecon
install_apt enum4linux
install_apt exploitdb searchsploit

# ── Python-based tools ────────────────────────────────────────────────────────
info "=== Installing Python tools ==="
install_pip theHarvester theHarvester
install_pip sherlock-project sherlock
install_pip arjun arjun
install_pip metagoofil metagoofil

# ── Go-based tools ────────────────────────────────────────────────────────────
info "=== Installing Go tools ==="
install_go_tool subfinder    "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
install_go_tool httpx        "github.com/projectdiscovery/httpx/cmd/httpx@latest"
install_go_tool nuclei       "github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
install_go_tool katana       "github.com/projectdiscovery/katana/cmd/katana@latest"
install_go_tool gau          "github.com/lc/gau/v2/cmd/gau@latest"
install_go_tool waybackurls  "github.com/tomnomnom/waybackurls@latest"
install_go_tool dalfox       "github.com/hahwul/dalfox/v2@latest"
install_go_tool ffuf         "github.com/ffuf/ffuf/v2@latest"
install_go_tool amass        "github.com/owasp-amass/amass/v4/...@master"
install_go_tool gowitness    "github.com/sensepost/gowitness@latest"
install_go_tool kxss         "github.com/Emoe/kxss@latest"
install_go_tool hakrevdns    "github.com/hakluke/hakrevdns@latest"
install_go_tool subjs        "github.com/lc/subjs@latest"

# ── linkfinder ────────────────────────────────────────────────────────────────
if ! which linkfinder &>/dev/null; then
    info "Installing LinkFinder..."
    git clone https://github.com/GerbenJavado/LinkFinder.git /opt/linkfinder 2>/dev/null || true
    pip3 install -r /opt/linkfinder/requirements.txt &>/dev/null
    ln -sf /opt/linkfinder/linkfinder.py /usr/local/bin/linkfinder
    chmod +x /usr/local/bin/linkfinder
    success "linkfinder installed"
fi

# ── cloud_enum ────────────────────────────────────────────────────────────────
if ! which cloud_enum &>/dev/null; then
    info "Installing cloud_enum..."
    git clone https://github.com/initstring/cloud_enum.git /opt/cloud_enum 2>/dev/null || true
    pip3 install -r /opt/cloud_enum/requirements.txt &>/dev/null
    ln -sf /opt/cloud_enum/cloud_enum.py /usr/local/bin/cloud_enum
    chmod +x /usr/local/bin/cloud_enum
    success "cloud_enum installed"
fi

# ── wfuzz ────────────────────────────────────────────────────────────────────
install_apt wfuzz

# ── Metasploit ───────────────────────────────────────────────────────────────
if ! which msfconsole &>/dev/null; then
    info "Installing Metasploit Framework..."
    curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb \
        > /tmp/msfinstall 2>/dev/null
    chmod +x /tmp/msfinstall
    /tmp/msfinstall &>/dev/null && success "Metasploit installed" || warn "Metasploit install failed — install manually"
fi

# ── Nuclei Templates ─────────────────────────────────────────────────────────
if [ ! -d "nuclei-templates" ]; then
    info "Cloning nuclei-templates..."
    git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates.git nuclei-templates 2>/dev/null
    success "nuclei-templates cloned"
fi

# ── Final verification ────────────────────────────────────────────────────────
echo ""
info "=== Running DARKWIN tool verification ==="
python3 -c "
import sys
sys.path.insert(0, '.')
from core.config_loader import load_config
from core.tool_loader import verify_all_tools
cfg = load_config()
verify_all_tools(cfg)
"

echo ""
success "Tool installation complete!"
