#!/usr/bin/env bash
# DARKWIN — One-command setup script
# Installs Python deps, all tools, and wordlists.

set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# 1. Virtual environment
if [ ! -d "venv" ]; then
    info "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# 2. Python dependencies
info "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install -e . -q
success "Python dependencies installed"

# 3. External tools
info "Installing external tools..."
bash scripts/install_tools.sh

# 4. Wordlists
info "Installing wordlists..."
bash scripts/install_wordlists.sh

success "DARKWIN setup complete! Run: darkwin --help"
