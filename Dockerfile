# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  DARKWIN v1.3.0 — Docker Image                                              ║
# ║  Advanced Automation Toolkit for Ethical Hackers & Bug Bounty Hunters       ║
# ║  Author: ARYAN AHIRWAR (VIPHACKER.100)                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝
#
# Build:     docker build -t darkwin:latest .
# Run CLI:   docker run -it --rm darkwin:latest --help
# Dashboard: docker run -p 5000:5000 -p 3000:3000 darkwin:latest dashboard

# ── Stage 1: Go tool builder ───────────────────────────────────────────────────
FROM golang:1.22-bookworm AS go-builder

ENV GOPATH=/root/go
ENV PATH="$PATH:/root/go/bin"
ENV CGO_ENABLED=0
ENV GOPROXY=https://proxy.golang.org,direct

RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest             && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest        && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest           && \
    go install github.com/projectdiscovery/dnsx/cmd/dnsx@latest               && \
    go install github.com/projectdiscovery/naabu/v2/cmd/naabu@latest          && \
    go install github.com/lc/gau/v2/cmd/gau@latest                            && \
    go install github.com/tomnomnom/waybackurls@latest                         && \
    go install github.com/hahwul/dalfox/v2@latest                             && \
    go install github.com/ffuf/ffuf/v2@latest                                  && \
    go install github.com/sensepost/gowitness@latest                           && \
    go install github.com/hakluke/hakrevdns@latest                             && \
    go install github.com/tomnomnom/kxss@latest                                && \
    go install github.com/lc/subjs@latest

# ── Stage 2: Node.js frontend builder ─────────────────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build/frontend
COPY dashboard/frontend/package*.json ./
RUN npm ci --prefer-offline

COPY dashboard/frontend/ .
RUN npm run build

# ── Stage 3: Final runtime image ──────────────────────────────────────────────
FROM kalilinux/kali-rolling:latest

LABEL maintainer="ARYAN AHIRWAR (VIPHACKER.100)"
LABEL org.opencontainers.image.title="DARKWIN"
LABEL org.opencontainers.image.description="Advanced Automation Toolkit for Ethical Hackers & Bug Bounty Hunters"
LABEL org.opencontainers.image.version="1.3.0"
LABEL org.opencontainers.image.source="https://github.com/VIPHACKER100/DarkWin-AATK"
LABEL org.opencontainers.image.licenses="MIT"

# ── System dependencies ────────────────────────────────────────────────────────
RUN apt-get update -qq && apt-get install -y --no-install-recommends \
    # Python runtime
    python3 python3-pip python3-venv \
    # Core utilities
    git curl wget bash make ca-certificates jq unzip \
    # Network / Recon tools
    nmap masscan whois dnsrecon enum4linux wfuzz \
    # Vulnerability scanners
    sqlmap \
    # OSINT tools
    theharvester \
    # Node.js runtime (dashboard frontend)
    nodejs npm \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── Copy Go binaries from builder ─────────────────────────────────────────────
COPY --from=go-builder /root/go/bin/ /usr/local/bin/

# ── Working directory ──────────────────────────────────────────────────────────
WORKDIR /opt/darkwin

# ── Copy project source ────────────────────────────────────────────────────────
COPY . .

# ── Python virtual environment ─────────────────────────────────────────────────
RUN python3 -m venv venv && \
    venv/bin/pip install --upgrade pip --quiet && \
    venv/bin/pip install -e ".[test]" --quiet

ENV PATH="/opt/darkwin/venv/bin:$PATH"
ENV PYTHONPATH="/opt/darkwin"

# ── Copy built Next.js frontend ────────────────────────────────────────────────
COPY --from=frontend-builder /build/frontend/.next         ./dashboard/frontend/.next
COPY --from=frontend-builder /build/frontend/public        ./dashboard/frontend/public
COPY --from=frontend-builder /build/frontend/node_modules  ./dashboard/frontend/node_modules
COPY --from=frontend-builder /build/frontend/package.json  ./dashboard/frontend/package.json

# ── Nuclei templates ───────────────────────────────────────────────────────────
RUN nuclei -update-templates -silent || true

# ── Runtime directories ────────────────────────────────────────────────────────
RUN mkdir -p logs reports results wordlists

# ── Expose ports ───────────────────────────────────────────────────────────────
# 5000 → Flask backend API
# 3000 → Next.js frontend dashboard
EXPOSE 5000 3000

# ── Health check ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:5000/api/health || exit 1

# ── Entry point ────────────────────────────────────────────────────────────────
ENTRYPOINT ["darkwin"]
CMD ["--help"]
