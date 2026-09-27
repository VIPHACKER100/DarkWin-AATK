# DarkWin-AATK Security Modules Catalog & Technical Reference

> Exhaustive technical specification for all security modules in **DarkWin - Automated Attack Toolkit (AATK)**.

---

## Catalog Index by Category

1. [Reconnaissance Modules (`modules/recon/`)](#1-reconnaissance-modules-modulesrecon)
2. [OSINT Modules (`modules/osint/`)](#2-osint-modules-modulesosint)
3. [Cloud Security Modules (`modules/cloud/`)](#3-cloud-security-modules-modulescloud)
4. [Web Discovery & Crawling Modules (`modules/web/`)](#4-web-discovery--crawling-modules-modulesweb)
5. [Network & Service Scanning Modules (`modules/network/`)](#5-network--service-scanning-modules-modulesnetwork)
6. [Vulnerability Testing Modules (`modules/vulnerabilities/`)](#6-vulnerability-testing-modules-modulesvulnerabilities)
7. [Web & API Fuzzing Modules (`modules/fuzzing/`)](#7-web--api-fuzzing-modules-modulesfuzzing)
8. [Exploitation Modules (`modules/exploitation/`)](#8-exploitation-modules-modulesexploitation)
9. [Post-Exploitation Modules (`modules/post_exploitation/`)](#9-post-exploitation-modules-modulespost_exploitation)
10. [Reporting Modules (`modules/reporting/`)](#10-reporting-modules-modulesreporting)

---

## Standard Module Contract

Every module in DarkWin-AATK conforms to a unified functional interface:

```python
def run(target: Target, config: dict, **kwargs) -> dict:
    """
    Executes security assessment logic.

    Args:
        target (Target): Target data model instance containing paths and metadata.
        config (dict): Master configuration dictionary loaded from YAML.
        **kwargs: Optional module-specific parameter overrides.

    Returns:
        dict: Standardized result object containing status, metrics, findings, and artifact paths.
    """
```

---

## 1. Reconnaissance Modules (`modules/recon/`)

### 1.1 `recon.subdomain_enum`
- **File:** `modules/recon/subdomain_enum.py`
- **Primary Binaries:** `subfinder`, `assetfinder`, `amass`, `sublist3r`
- **Description:** Aggregates passive subdomain queries across public certificate transparency logs, DNS databases, and search engines. Deduplicates output and writes unique FQDNs.
- **Artifact Generated:** `recon/subdomains.txt`
- **Result Schema:** `{"status": "SUCCESS", "count": 142, "file": "path/to/subdomains.txt"}`

### 1.2 `recon.dns_bruteforce`
- **File:** `modules/recon/dns_bruteforce.py`
- **Primary Binaries:** `puredns`, `massdns`, Python `dnspython`
- **Description:** Performs high-speed active DNS resolution and dictionary brute-forcing against wildcards, identifying live `A`, `AAAA`, and `CNAME` records.
- **Artifact Generated:** `recon/dns_resolved.json`, `recon/live_subdomains.txt`

### 1.3 `recon.reverse_ip`
- **File:** `modules/recon/reverse_ip.py`
- **Description:** Identifies virtual hosts and other domains co-located on the same server IP via reverse DNS queries and public API lookups.
- **Artifact Generated:** `recon/reverse_ip.json`

### 1.4 `recon.whois_lookup`
- **File:** `modules/recon/whois_lookup.py`
- **Description:** Queries registry databases to extract registrar name, creation/expiry timestamps, nameservers, and registrant contact data.
- **Artifact Generated:** `recon/whois.json`

### 1.5 `recon.asn_lookup`
- **File:** `modules/recon/asn_lookup.py`
- **Description:** Resolves target IP addresses to Autonomous System Numbers (ASN), BGP routing prefixes, organization names, and IP ranges.
- **Artifact Generated:** `recon/asn_info.json`

### 1.6 `recon.github_dorking`
- **File:** `modules/recon/github_dorking.py`
- **Description:** Searches GitHub repositories and commits for leaked credentials, private keys, API secrets, and internal staging endpoints.
- **Artifact Generated:** `recon/github_leaks.json`

### 1.7 `recon.s3_bucket_scan`
- **File:** `modules/recon/s3_bucket_scan.py`
- **Description:** Generates permutation-based bucket names (e.g. `target-dev`, `target-backup`) and probes for public AWS S3 bucket permissions.
- **Artifact Generated:** `recon/s3_buckets.json`

---

## 2. OSINT Modules (`modules/osint/`)

### 2.1 `osint.email_harvester`
- **File:** `modules/osint/email_harvester.py`
- **Primary Tools:** `theHarvester`, Hunter.io API, Search Engine Scraping
- **Description:** Harvests corporate email addresses, usernames, and domain aliases associated with the target domain.
- **Artifact Generated:** `osint/emails.json`

### 2.2 `osint.metadata_scraper`
- **File:** `modules/osint/metadata_scraper.py`
- **Primary Binary:** `exiftool`
- **Description:** Downloads public documents (`.pdf`, `.docx`, `.xlsx`) and parses EXIF/metadata for user names, software versions, and local paths.
- **Artifact Generated:** `osint/metadata_findings.json`

### 2.3 `osint.social_media_enum`
- **File:** `modules/osint/social_media_enum.py`
- **Description:** Identifies brand handles, company profiles, and employee presences across LinkedIn, Twitter/X, GitHub, and Facebook.
- **Artifact Generated:** `osint/social_profiles.json`

### 2.4 `osint.breach_lookup`
- **File:** `modules/osint/breach_lookup.py`
- **Description:** Cross-references harvested emails against known data breaches and publicly dumped credential caches.
- **Artifact Generated:** `osint/breaches.json`

---

## 3. Cloud Security Modules (`modules/cloud/`)

### 3.1 `cloud.cloud_enum`
- **File:** `modules/cloud/cloud_enum.py`
- **Description:** Audits multi-cloud asset exposures:
  - **AWS:** Amazon S3 Buckets, CloudFront distributions
  - **GCP:** Google Cloud Storage buckets, Firebase apps
  - **Azure:** Azure Blob storage containers, App Services
- **Artifact Generated:** `cloud/cloud_assets.json`

---

## 4. Web Discovery & Crawling Modules (`modules/web/`)

### 4.1 `web.url_collector`
- **File:** `modules/web/url_collector.py`
- **Primary Binaries:** `waybackurls`, `gau`
- **Description:** Extracts passive web archive histories from AlienVault OTX, Wayback Machine, and CommonCrawl to discover historical and unlinked endpoints.
- **Artifact Generated:** `web/historical_urls.txt`

### 4.2 `web.crawler`
- **File:** `modules/web/crawler.py`
- **Primary Binaries:** `katana`, `gospider`
- **Description:** Actively crawls modern web applications, following hyperlinks, extracting forms, executing JavaScript, and logging dynamic routes.
- **Artifact Generated:** `web/crawled_urls.txt`

### 4.3 `web.js_parser`
- **File:** `modules/web/js_parser.py`
- **Description:** Downloads and statically parses JavaScript files, extracting hardcoded tokens, API endpoints, hidden secrets, and source map references.
- **Artifact Generated:** `web/js_endpoints.txt`, `web/js_secrets.json`

### 4.4 `web.parameter_finder`
- **File:** `modules/web/parameter_finder.py`
- **Primary Binary:** `arjun`
- **Description:** Probes web endpoints for hidden GET and POST parameter names vulnerable to parameter tampering or injection.
- **Artifact Generated:** `web/discovered_parameters.json`

---

## 5. Network & Service Scanning Modules (`modules/network/`)

### 5.1 `network.port_scanner`
- **File:** `modules/network/port_scanner.py`
- **Primary Binaries:** `nmap`, `masscan`
- **Description:** Scans target IP or domain for open TCP and UDP ports using customizable scan rates, ports, and timing profiles.
- **Artifact Generated:** `network/open_ports.txt`, `network/nmap_scan.xml`

### 5.2 `network.service_enum`
- **File:** `modules/network/service_enum.py`
- **Primary Binary:** `nmap` (`-sV -sC`)
- **Description:** Determines software names and exact versions running on discovered open ports, running Nmap NSE service scripts.
- **Artifact Generated:** `network/services.json`

### 5.3 `network.smb_enum`
- **File:** `modules/network/smb_enum.py`
- **Primary Binaries:** `smbclient`, `enum4linux`
- **Description:** Queries Windows SMB services (ports 139/445) for anonymous share access, user listings, domain names, and password policies.
- **Artifact Generated:** `network/smb_audit.json`

### 5.4 `network.ftp_enum`
- **File:** `modules/network/ftp_enum.py`
- **Description:** Verifies anonymous login access on port 21, crawls readable directory trees, and flags banner vulnerabilities.
- **Artifact Generated:** `network/ftp_audit.json`

### 5.5 `network.ssh_enum`
- **File:** `modules/network/ssh_enum.py`
- **Description:** Identifies SSH server versions, weak ciphers, outdated key exchange algorithms, and checks default credential sets.
- **Artifact Generated:** `network/ssh_audit.json`

---

## 6. Vulnerability Testing Modules (`modules/vulnerabilities/`)

### 6.1 `vulnerabilities.reflected_xss`
- **File:** `modules/vulnerabilities/xss/reflected_xss.py`
- **Primary Binary:** `dalfox`
- **Description:** Tests parameters for reflected Cross-Site Scripting by evaluating reflection contexts and payload execution.
- **Artifact Generated:** `vulns/reflected_xss.json`

### 6.2 `vulnerabilities.dom_xss`
- **File:** `modules/vulnerabilities/xss/dom_xss.py`
- **Description:** Analyzes JavaScript code for DOM-based XSS vulnerabilities, tracing untrusted sources (`document.location`, `window.name`) to dangerous sinks (`innerHTML`, `eval`).
- **Artifact Generated:** `vulns/dom_xss.json`

### 6.3 `vulnerabilities.sqli_detector`
- **File:** `modules/vulnerabilities/sqli/sqli_detector.py`
- **Primary Binary:** `sqlmap`
- **Description:** Tests parameters for SQL injection vulnerabilities using error-based and boolean-based heuristic probes.
- **Artifact Generated:** `vulns/sqli_findings.json`

### 6.4 `vulnerabilities.blind_sqli`
- **File:** `modules/vulnerabilities/sqli/blind_sqli.py`
- **Description:** Detects time-based blind SQL injection using delay payloads across MySQL, PostgreSQL, MSSQL, Oracle, and SQLite.
- **Artifact Generated:** `vulns/blind_sqli.json`

### 6.5 `vulnerabilities.lfi_scanner`
- **File:** `modules/vulnerabilities/lfi/lfi_scanner.py`
- **Description:** Injects path traversal strings (`../../../../etc/passwd`, `..\..\..\windows\win.ini`) and PHP wrappers to identify Local File Inclusion vulnerabilities.
- **Artifact Generated:** `vulns/lfi_findings.json`

### 6.6 `vulnerabilities.ssrf_tester`
- **File:** `modules/vulnerabilities/ssrf/ssrf_tester.py`
- **Description:** Probes for Server-Side Request Forgery by injecting loopback addresses (`127.0.0.1`), cloud metadata endpoints (`169.254.169.254`), and out-of-band callback URLs.
- **Artifact Generated:** `vulns/ssrf_findings.json`

### 6.7 `vulnerabilities.rce_scanner`
- **File:** `modules/vulnerabilities/rce/rce_scanner.py`
- **Description:** Injects command-chaining operators and blind time-delay commands to detect Remote Code Execution vulnerabilities.
- **Artifact Generated:** `vulns/rce_findings.json`

### 6.8 `vulnerabilities.csrf_detector`
- **File:** `modules/vulnerabilities/csrf/csrf_detector.py`
- **Description:** Checks web forms and sensitive actions for missing anti-CSRF tokens, SameSite cookie configurations, and permissive CORS policies.
- **Artifact Generated:** `vulns/csrf_findings.json`

### 6.9 `vulnerabilities.idor_scanner`
- **File:** `modules/vulnerabilities/idor/idor_scanner.py`
- **Description:** Tests authorization boundaries by mutating object IDs and checking for Insecure Direct Object Reference vulnerabilities.
- **Artifact Generated:** `vulns/idor_findings.json`

---

## 7. Web & API Fuzzing Modules (`modules/fuzzing/`)

### 7.1 `fuzzing.directory_fuzzer`
- **File:** `modules/fuzzing/directory_fuzzer.py`
- **Primary Binary:** `ffuf`
- **Description:** Discovers hidden web directories, administrative portals, backup files, and sensitive configurations using wordlists.
- **Artifact Generated:** `fuzzing/directories.json`

### 7.2 `fuzzing.api_fuzzer`
- **File:** `modules/fuzzing/api_fuzzer.py`
- **Description:** Fuzzes API endpoints using HTTP method tampering (`PUT`, `DELETE`, `PATCH`), malformed JSON payloads, and parameter injection.
- **Artifact Generated:** `fuzzing/api_endpoints.json`

### 7.3 `fuzzing.parameter_fuzzer`
- **File:** `modules/fuzzing/parameter_fuzzer.py`
- **Primary Binary:** `ffuf`
- **Description:** High-speed parameter fuzzing against GET and POST endpoints to discover undocumented parameters.
- **Artifact Generated:** `fuzzing/parameter_fuzz.json`

---

## 8. Exploitation Modules (`modules/exploitation/`)

### 8.1 `exploitation.exploit_runner`
- **File:** `modules/exploitation/exploit_runner.py`
- **Primary Binary:** `searchsploit`
- **Description:** Queries Exploit-DB for public exploits matching discovered software versions and automates verification.
- **Artifact Generated:** `exploitation/matching_exploits.json`

### 8.2 `exploitation.metasploit_runner`
- **File:** `modules/exploitation/metasploit_runner.py`
- **Primary Tool:** `pymetasploit3` / `msfconsole`
- **Description:** Connects to the Metasploit RPC daemon, configures module payloads, and tests known exploitable vulnerabilities.
- **Artifact Generated:** `exploitation/msf_results.json`

### 8.3 `exploitation.payload_generator`
- **File:** `modules/exploitation/payload_generator.py`
- **Primary Binary:** `msfvenom`
- **Description:** Generates reverse shells and staged/stageless payloads across multiple formats (`elf`, `exe`, `php`, `asp`, `war`).
- **Artifact Generated:** `exploitation/payloads/`

---

## 9. Post-Exploitation Modules (`modules/post_exploitation/`)

### 9.1 `post_exploitation.privesc_checker`
- **File:** `modules/post_exploitation/privesc_checker.py`
- **Primary Tools:** LinPEAS / WinPEAS
- **Description:** Audits compromised hosts for privilege escalation vectors, including SUID binaries, misconfigured sudoers, and kernel vulnerabilities.
- **Artifact Generated:** `post_exploitation/privesc_report.txt`

### 9.2 `post_exploitation.lateral_movement`
- **File:** `modules/post_exploitation/lateral_movement.py`
- **Primary Tool:** Impacket
- **Description:** Tests discovered credentials across network segments using pass-the-hash, WMI, and WinRM protocols.
- **Artifact Generated:** `post_exploitation/lateral_movement.json`

### 9.3 `post_exploitation.persistence_auditor`
- **File:** `modules/post_exploitation/persistence_auditor.py`
- **Description:** Audits compromised systems for persistence mechanisms, including cron jobs, services, SSH keys, and scheduled tasks.
- **Artifact Generated:** `post_exploitation/persistence_findings.json`

---

## 10. Reporting Modules (`modules/reporting/`)

### 10.1 `reporting.report_builder`
- **File:** `modules/reporting/report_builder.py`
- **Description:** Aggregates findings from all executed modules, calculates severity metrics, and structures data for export.
- **Artifact Generated:** `reports/findings.json`

### 10.2 `reporting.html_report`
- **File:** `modules/reporting/html_report.py`
- **Description:** Renders an interactive, responsive HTML report from the Jinja2 template (`templates/report.html.j2`).
- **Artifact Generated:** `reports/report.html`
