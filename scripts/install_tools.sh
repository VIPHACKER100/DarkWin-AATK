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
    local pip_cmd="pip3"
    if [ -n "${VIRTUAL_ENV:-}" ] && [ -f "$VIRTUAL_ENV/bin/pip" ]; then
        pip_cmd="$VIRTUAL_ENV/bin/pip"
    elif [[ $EUID -eq 0 ]] && [ -f "$(pwd)/venv/bin/pip" ]; then
        pip_cmd="$(pwd)/venv/bin/pip3"
    fi
        info "Installing $pkg via $pip_cmd..."
        $pip_cmd install "$pkg" &>/dev/null && success "$pkg installed" || error "Failed to install $pkg"
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
# When run as root, preserve the original user's GOPATH for correct binary location
if [[ $EUID -eq 0 ]] && [ -n "${SUDO_USER:-}" ]; then
    ORIG_USER_HOME="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
    export GOPATH="$ORIG_USER_HOME/go"
    export PATH="$PATH:$GOPATH/bin"
fi

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

# ── Symlink Go binaries to /usr/local/bin when run as root ────────────────────
if [[ $EUID -eq 0 ]]; then
    for dir in "$GOPATH/bin" "/root/go/bin"; do
        [ -d "$dir" ] || continue
        for binary in "$dir/"*; do
            [ -f "$binary" ] && ln -sf "$binary" /usr/local/bin/ 2>/dev/null || true
        done
    done
    # Re-check after symlink — try go install for anything still missing
    for tool in subfinder gau dalfox gowitness subjs waybackurls kxss hakrevdns; do
        which "$tool" &>/dev/null && continue
        info "Installing $tool via go install..."
        case "$tool" in
            subfinder)   go install "github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest" 2>/dev/null ;;
            gau)         go install "github.com/lc/gau/v2/cmd/gau@latest" 2>/dev/null ;;
            dalfox)      go install "github.com/hahwul/dalfox/v2@latest" 2>/dev/null ;;
            gowitness)   go install "github.com/sensepost/gowitness@latest" 2>/dev/null ;;
            subjs)       go install "github.com/lc/subjs@latest" 2>/dev/null ;;
            waybackurls) go install "github.com/tomnomnom/waybackurls@latest" 2>/dev/null ;;
            kxss)        go install "github.com/Emoe/kxss@latest" 2>/dev/null ;;
            hakrevdns)   go install "github.com/hakluke/hakrevdns@latest" 2>/dev/null ;;
        esac
        # Symlink again after fresh install
        for dir in "$GOPATH/bin" "/root/go/bin"; do
            [ -d "$dir" ] || continue
            for binary in "$dir/"*; do
                [ -f "$binary" ] && ln -sf "$binary" /usr/local/bin/ 2>/dev/null || true
            done
        done
        which "$tool" &>/dev/null && success "$tool installed" || error "Failed to install $tool"
    done
    success "Go binaries symlinked to /usr/local/bin/"
fi

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
