# DARKWIN — Docker Image
# Based on Kali Linux rolling for full tool compatibility.
FROM kalilinux/kali-rolling:latest

LABEL maintainer="DARKWIN Project"
LABEL description="Advanced Automation Toolkit for Ethical Hackers"

# ── System dependencies ───────────────────────────────────────────────────────
RUN apt-get update -qq && apt-get install -y \
    python3 python3-pip python3-venv \
    git curl wget bash make \
    nmap masscan sqlmap whois dnsrecon enum4linux wfuzz \
    golang-go \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /opt/darkwin

# ── Copy project ──────────────────────────────────────────────────────────────
COPY . .

# ── Python environment ────────────────────────────────────────────────────────
RUN python3 -m venv venv && \
    venv/bin/pip install --upgrade pip -q && \
    venv/bin/pip install -r requirements.txt -q && \
    venv/bin/pip install -e . -q

ENV PATH="/opt/darkwin/venv/bin:$PATH"

# ── Go tools ─────────────────────────────────────────────────────────────────
ENV GOPATH=/root/go
ENV PATH="$PATH:/root/go/bin"

RUN go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install github.com/projectdiscovery/katana/cmd/katana@latest && \
    go install github.com/lc/gau/v2/cmd/gau@latest && \
    go install github.com/tomnomnom/waybackurls@latest && \
    go install github.com/hahwul/dalfox/v2@latest && \
    go install github.com/ffuf/ffuf/v2@latest && \
    go install github.com/sensepost/gowitness@latest

# ── Nuclei templates ──────────────────────────────────────────────────────────
RUN nuclei -update-templates -silent || true

# ── Directory structure ───────────────────────────────────────────────────────
RUN mkdir -p logs reports wordlists

# ── Entry point ───────────────────────────────────────────────────────────────
ENTRYPOINT ["darkwin"]
CMD ["--help"]
