#!/usr/bin/env bash
# DARKWIN — Wordlists Installer
# Clones SecLists and PayloadsAllTheThings into the wordlists/ directory.

set -euo pipefail

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

info()    { echo -e "${CYAN}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }

WORDLISTS_DIR="wordlists"
mkdir -p "$WORDLISTS_DIR"

# SecLists
if [ ! -d "$WORDLISTS_DIR/SecLists" ]; then
    info "Cloning SecLists (this may take a while)..."
    git clone --depth 1 https://github.com/danielmiessler/SecLists.git \
        "$WORDLISTS_DIR/SecLists"
    success "SecLists cloned → $WORDLISTS_DIR/SecLists"
else
    info "SecLists already present. Pulling updates..."
    git -C "$WORDLISTS_DIR/SecLists" pull --rebase --quiet
    success "SecLists updated"
fi

# PayloadsAllTheThings
if [ ! -d "$WORDLISTS_DIR/PayloadsAllTheThings" ]; then
    info "Cloning PayloadsAllTheThings..."
    git clone --depth 1 https://github.com/swisskyrepo/PayloadsAllTheThings.git \
        "$WORDLISTS_DIR/PayloadsAllTheThings"
    success "PayloadsAllTheThings cloned → $WORDLISTS_DIR/PayloadsAllTheThings"
else
    info "PayloadsAllTheThings already present. Pulling updates..."
    git -C "$WORDLISTS_DIR/PayloadsAllTheThings" pull --rebase --quiet
    success "PayloadsAllTheThings updated"
fi

success "All wordlists ready in $WORDLISTS_DIR/"
