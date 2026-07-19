#!/usr/bin/env bash
# DARKWIN — Tool Installer (hardened)
# Installs all required external tools for the DARKWIN toolkit.
# Run as root or with sudo on Kali Linux / Debian-based systems.
#
# Usage:
#   sudo bash scripts/install_tools.sh                  # install everything
#   sudo bash scripts/install_tools.sh --only subfinder,gau,dalfox   # install just these
#   sudo bash scripts/install_tools.sh --missing         # re-run doctor first, install only what's missing
#
# All install output is logged to install_tools.log. On failure the last
# lines of the relevant command's output are printed immediately instead of
# being silently discarded, so you can see WHY a tool failed.

set -uo pipefail   # note: no -e — one tool failing must not kill the run

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

LOG_FILE="$(pwd)/install_tools.log"
: > "$LOG_FILE"

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[WARN]${NC}  $*"; }
error()   { echo -e "${RED}[ERR]${NC}   $*"; }

FAILED_TOOLS=()

check_root() {
    if [[ $EUID -ne 0 ]]; then
        warn "Not running as root. Some installs may fail."
        warn "Re-run with: sudo bash scripts/install_tools.sh"
    fi
}

_check() { python3 -c "import shutil; exit(0 if shutil.which('$1') else 1)"; }

# Run a command, log everything, and on failure print the tail of the log
# instead of swallowing it. Returns the command's exit code.
_run_logged() {
    local label="$1"; shift
    echo "===== $label =====" >> "$LOG_FILE"
    if "$@" >>"$LOG_FILE" 2>&1; then
        return 0
    else
        local rc=$?
        error "$label failed (exit $rc) — last output:"
        tail -n 8 "$LOG_FILE" | sed 's/^/    /'
        return $rc
    fi
}

# ── Go environment: set ONCE, consistently, and pin it into `go env` itself ──
# so every subprocess (including ones that don't inherit our exported vars)
# resolves to the same GOPATH/GOBIN. This fixes the split-brain between the
# early "$HOME/go" and the later SUDO_USER-based reassignment.
setup_go_env() {
    if ! which go &>/dev/null; then
        info "Installing Go..."
        _run_logged "apt install golang-go" apt-get install -y golang-go
    fi

    local target_home="$HOME"
    if [[ $EUID -eq 0 && -n "${SUDO_USER:-}" ]]; then
        target_home="$(getent passwd "$SUDO_USER" | cut -d: -f6)"
    fi

    export GOPATH="$target_home/go"
    export GOBIN="$GOPATH/bin"
    mkdir -p "$GOBIN"
    export PATH="$PATH:$GOBIN"

    # Pin it so `go install` uses this even if a subshell drops our env vars.
    go env -w GOPATH="$GOPATH" 2>/dev/null || true
    go env -w GOBIN="$GOBIN" 2>/dev/null || true

    info "Go tools will install to: $GOBIN"
}

install_go_tool() {
    local name="$1"
    local pkg="$2"
    if _check "$name"; then
        success "$name already installed"
        return 0
    fi

    info "Installing $name via go install..."
    local attempt ok=0
    for attempt in 1 2 3; do
        if _run_logged "go install $pkg (attempt $attempt)" go install "$pkg"; then
            ok=1
            break
        fi
        if [[ $attempt -eq 1 ]]; then
            warn "$name: retrying with GOPROXY=direct GOSUMDB=off (common fix for blocked module proxy)"
            GOPROXY=direct GOSUMDB=off _run_logged "go install $pkg (direct proxy, attempt $attempt)" go install "$pkg" && { ok=1; break; }
        fi
        sleep 2
    done

    # Symlink into /usr/local/bin so it's on every user's PATH, not just GOBIN's owner.
    if [[ $EUID -eq 0 && -f "$GOBIN/$name" ]]; then
        ln -sf "$GOBIN/$name" /usr/local/bin/"$name"
        # Hand ownership back to the invoking user if we ran under sudo,
        # otherwise root ends up owning files in the user's home GOPATH.
        if [[ -n "${SUDO_USER:-}" ]]; then
            chown "$SUDO_USER":"$SUDO_USER" "$GOBIN/$name" 2>/dev/null || true
        fi
    fi

    if _check "$name"; then
        success "$name installed"
    else
        error "Failed to install $name after 3 attempts — see install_tools.log"
        FAILED_TOOLS+=("$name")
    fi
}

install_apt() {
    local pkg="$1"
    local binary="${2:-$1}"
    if _check "$binary"; then
        success "$binary already installed"
        return 0
    fi
    info "Installing $pkg via apt..."
    if _run_logged "apt install $pkg" apt-get install -y "$pkg" && _check "$binary"; then
        success "$pkg installed"
    else
        error "Failed to install $pkg"
        FAILED_TOOLS+=("$binary")
    fi
    if [[ $EUID -eq 0 ]] && [ -f "/root/go/bin/$binary" ] && ! _check "$binary"; then
        ln -sf "/root/go/bin/$binary" /usr/local/bin/ 2>/dev/null || true
    fi
}

install_pip() {
    local pkg="$1"
    local binary="${2:-$1}"
    if _check "$binary"; then
        success "$binary already installed"
        return 0
    fi
    local pip_cmd="pip3"
    if [ -n "${VIRTUAL_ENV:-}" ] && [ -f "$VIRTUAL_ENV/bin/pip" ]; then
        pip_cmd="$VIRTUAL_ENV/bin/pip"
    elif [[ $EUID -eq 0 ]] && [ -f "$(pwd)/venv/bin/pip" ]; then
        pip_cmd="$(pwd)/venv/bin/pip3"
    fi
    info "Installing $pkg via $pip_cmd..."
    if _run_logged "$pip_cmd install $pkg" "$pip_cmd" install "$pkg" --break-system-packages && _check "$binary"; then
        success "$pkg installed"
    else
        error "Failed to install $pkg"
        FAILED_TOOLS+=("$binary")
    fi
}

# metagoofil has no reliable PyPI package that ships a working binary —
# it must come from GitHub, same pattern as linkfinder/cloud_enum below.
install_metagoofil() {
    if _check metagoofil; then
        success "metagoofil already installed"
        return 0
    fi
    info "Installing metagoofil from GitHub..."
    if [ ! -d /opt/metagoofil ]; then
        _run_logged "clone metagoofil" git clone https://github.com/laramies/metagoofil.git /opt/metagoofil
    fi
    _run_logged "metagoofil requirements" pip3 install -r /opt/metagoofil/requirements.txt --break-system-packages
    cat > /usr/local/bin/metagoofil <<'EOF'
#!/usr/bin/env bash
exec python3 /opt/metagoofil/metagoofil.py "$@"
EOF
    chmod +x /usr/local/bin/metagoofil
    if _check metagoofil; then
        success "metagoofil installed"
    else
        error "Failed to install metagoofil — see install_tools.log"
        FAILED_TOOLS+=("metagoofil")
    fi
}

install_linkfinder() {
    if _check linkfinder; then
        success "linkfinder already installed"
        return 0
    fi
    info "Installing LinkFinder..."
    [ -d /opt/linkfinder ] || _run_logged "clone linkfinder" git clone https://github.com/GerbenJavado/LinkFinder.git /opt/linkfinder
    _run_logged "linkfinder requirements" pip3 install -r /opt/linkfinder/requirements.txt --break-system-packages
    ln -sf /opt/linkfinder/linkfinder.py /usr/local/bin/linkfinder
    chmod +x /usr/local/bin/linkfinder
    if _check linkfinder; then
        success "linkfinder installed"
    else
        error "Failed to install linkfinder — see install_tools.log"
        FAILED_TOOLS+=("linkfinder")
    fi
}

install_cloud_enum() {
    if _check cloud_enum; then
        success "cloud_enum already installed"
        return 0
    fi
    info "Installing cloud_enum..."
    [ -d /opt/cloud_enum ] || _run_logged "clone cloud_enum" git clone https://github.com/initstring/cloud_enum.git /opt/cloud_enum
    _run_logged "cloud_enum requirements" pip3 install -r /opt/cloud_enum/requirements.txt --break-system-packages
    ln -sf /opt/cloud_enum/cloud_enum.py /usr/local/bin/cloud_enum
    chmod +x /usr/local/bin/cloud_enum
    if _check cloud_enum; then
        success "cloud_enum installed"
    else
        error "Failed to install cloud_enum — see install_tools.log"
        FAILED_TOOLS+=("cloud_enum")
    fi
}

install_metasploit() {
    if _check msfconsole; then
        success "msfconsole already installed"
        return 0
    fi
    info "Installing Metasploit Framework..."
    curl -fsSL https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb \
        > /tmp/msfinstall
    chmod +x /tmp/msfinstall
    if _run_logged "msfinstall" /tmp/msfinstall; then
        success "Metasploit installed"
    else
        warn "Metasploit install failed — install manually"
        FAILED_TOOLS+=("msfconsole")
    fi
}

# ── Tool registry ─────────────────────────────────────────────────────────
declare -A GO_TOOLS=(
    [subfinder]="github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"
    [httpx]="github.com/projectdiscovery/httpx/cmd/httpx@latest"
    [nuclei]="github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
    [katana]="github.com/projectdiscovery/katana/cmd/katana@latest"
    [gau]="github.com/lc/gau/v2/cmd/gau@latest"
    [waybackurls]="github.com/tomnomnom/waybackurls@latest"
    [dalfox]="github.com/hahwul/dalfox/v2@latest"
    [ffuf]="github.com/ffuf/ffuf/v2@latest"
    [amass]="github.com/owasp-amass/amass/v4/...@master"
    [gowitness]="github.com/sensepost/gowitness@latest"
    [kxss]="github.com/Emoe/kxss@latest"
    [hakrevdns]="github.com/hakluke/hakrevdns@latest"
    [subjs]="github.com/lc/subjs@latest"
)
declare -A APT_TOOLS=(
    [nmap]="nmap" [masscan]="masscan" [sqlmap]="sqlmap" [whois]="whois"
    [dnsrecon]="dnsrecon" [enum4linux]="enum4linux" [wfuzz]="wfuzz"
)
declare -A PIP_TOOLS=(
    [theHarvester]="theHarvester" [sherlock]="sherlock-project" [arjun]="arjun"
)

run_all() {
    local only_filter="${1:-}"   # comma-separated tool names, or empty for all

    _wanted() {
        [[ -z "$only_filter" ]] && return 0
        [[ ",$only_filter," == *",$1,"* ]]
    }

    check_root
    info "Updating apt package index..."
    _run_logged "apt update" apt-get update -qq
    setup_go_env

    info "=== apt-based tools ==="
    for t in "${!APT_TOOLS[@]}"; do _wanted "$t" && install_apt "${APT_TOOLS[$t]}" "$t"; done
    _wanted "exploitdb" && install_apt exploitdb searchsploit

    info "=== Python tools ==="
    for t in "${!PIP_TOOLS[@]}"; do _wanted "$t" && install_pip "${PIP_TOOLS[$t]}" "$t"; done
    _wanted "metagoofil" && install_metagoofil

    info "=== Go tools ==="
    for t in "${!GO_TOOLS[@]}"; do _wanted "$t" && install_go_tool "$t" "${GO_TOOLS[$t]}"; done

    _wanted "linkfinder" && install_linkfinder
    _wanted "cloud_enum" && install_cloud_enum
    _wanted "msfconsole" && install_metasploit

    if [[ -z "$only_filter" ]] && [ ! -d "nuclei-templates" ]; then
        info "Cloning nuclei-templates..."
        _run_logged "clone nuclei-templates" git clone --depth 1 https://github.com/projectdiscovery/nuclei-templates.git nuclei-templates
        success "nuclei-templates cloned"
    fi
}

# ── Entry point ───────────────────────────────────────────────────────────
ONLY=""
if [[ "${1:-}" == "--only" ]]; then
    ONLY="$2"
elif [[ "${1:-}" == "--missing" ]]; then
    info "Detecting missing tools via darkwin doctor..."
    ONLY="$(darkwin doctor 2>/dev/null | grep -oP '(?<=missing: ).*' | tr -d ' ')"
    if [[ -z "$ONLY" ]]; then
        warn "Could not parse missing tools from 'darkwin doctor' — installing everything instead."
    else
        info "Missing: $ONLY"
    fi
fi

run_all "$ONLY"

echo ""
if [[ ${#FAILED_TOOLS[@]} -eq 0 ]]; then
    success "All requested tools installed successfully!"
else
    error "The following tools still failed: ${FAILED_TOOLS[*]}"
    warn "Full logs are in $LOG_FILE — check the tail printed above each failure for the actual cause"
    warn "(most common causes: GOPROXY blocked by your network, or GitHub rate-limiting on cloned repos)"
fi

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
