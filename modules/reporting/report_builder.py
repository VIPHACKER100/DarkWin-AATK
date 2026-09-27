"""
DARKWIN — Reporting | Report Builder
Walks the scan output directory and aggregates all result files into a structured dict
with executive assessment metrics and categorized intelligence.
"""

import json
import os
import re
from pathlib import Path
from core.logger import get_logger


def collect_results(output_dir: str) -> dict:
    """
    Walk the output directory tree and collect all .txt, .json, .csv, and .log result files.

    Returns a structured dictionary keyed by module name, supplemented with
    categorized telemetry (subdomains, endpoints, ports, vulnerabilities, OSINT, stats).

    Args:
        output_dir: Root directory of the scan output.

    Returns:
        Dictionary: {
            "target": str,
            "output_dir": str,
            "modules": dict,
            "subdomains": list,
            "urls": list,
            "ports": list,
            "emails": list,
            "findings": list,
            "osint": dict,
            "logs": dict,
            "stats": dict,
            "risk_level": str,
            "risk_score": int
        }
    """
    log = get_logger(tool_name="report_builder", target=output_dir)

    out_path = Path(output_dir).resolve()
    target_name = out_path.parent.name if out_path.parent.name not in ("reports", "results", "") else out_path.name

    result = {
        "target": target_name,
        "output_dir": str(output_dir),
        "modules": {},
        "subdomains": [],
        "urls": [],
        "ports": [],
        "emails": [],
        "findings": [],
        "osint": {},
        "logs": {},
        "stats": {
            "subdomains_count": 0,
            "urls_count": 0,
            "ports_count": 0,
            "emails_count": 0,
            "artifacts_count": 0,
            "findings_count": {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0},
            "total_findings": 0,
        },
        "risk_level": "SECURE",
        "risk_score": 0,
    }

    if not out_path.exists():
        log.warning(f"Output directory not found: {output_dir}")
        return result

    subdomains_set = set()
    urls_set = set()
    emails_set = set()
    findings_list = []
    artifacts_count = 0

    for root, dirs, files in os.walk(out_path):
        for filename in sorted(files):
            file_path = Path(root) / filename
            if filename == "report.html":
                continue

            artifacts_count += 1
            module_key = file_path.stem.replace("-", "_")

            # Collect log files separately so they don't pollute modules but remain accessible
            if filename.endswith(".log"):
                try:
                    log_text = file_path.read_text(encoding="utf-8", errors="replace")
                    result["logs"][module_key] = {
                        "file": str(file_path),
                        "size": file_path.stat().st_size,
                        "lines": len(log_text.splitlines()),
                        "content": log_text[:10000]
                    }
                except Exception:
                    pass
                continue

            # Disambiguate if key already exists
            if module_key in result["modules"]:
                rel = str(file_path.relative_to(out_path)).replace(os.sep, "_")
                module_key = rel.replace(".", "_")

            content = None
            file_type = "txt"

            if filename.endswith(".json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = json.load(f)
                    file_type = "json"
                except (json.JSONDecodeError, UnicodeDecodeError):
                    content = file_path.read_text(encoding="utf-8", errors="replace")
                    file_type = "txt"

            elif filename.endswith((".txt", ".xml", ".csv")):
                content = file_path.read_text(encoding="utf-8", errors="replace")
                file_type = "txt"
            else:
                continue

            result["modules"][module_key] = {
                "file": str(file_path),
                "type": file_type,
                "content": content,
            }
            log.info(f"Collected: {file_path.name} → key: {module_key}")

            # --- Extract Categorized Intelligence ---
            lower_name = filename.lower()

            # Subdomains
            if "subdomain" in lower_name or lower_name in ("subs.txt", "hosts.txt"):
                if isinstance(content, str):
                    for line in content.splitlines():
                        sub = line.strip()
                        if sub and not sub.startswith("#") and "." in sub:
                            subdomains_set.add(sub)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, str) and "." in item:
                            subdomains_set.add(item.strip())
                        elif isinstance(item, dict) and "host" in item:
                            subdomains_set.add(str(item["host"]).strip())

            # URLs & Crawled Endpoints
            if "url" in lower_name or "gau" in lower_name or "wayback" in lower_name or "katana" in lower_name:
                if isinstance(content, str):
                    for line in content.splitlines():
                        url = line.strip()
                        if url and (url.startswith("http://") or url.startswith("https://")):
                            urls_set.add(url)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, str) and item.startswith("http"):
                            urls_set.add(item.strip())

            # OSINT Emails
            if "email" in lower_name:
                if isinstance(content, str):
                    found_emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", content)
                    emails_set.update(found_emails)
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, str) and "@" in item:
                            emails_set.add(item.strip())
                elif isinstance(content, dict):
                    for e in content.get("emails", []):
                        if isinstance(e, str):
                            emails_set.add(e.strip())

            # Specific OSINT modules
            if lower_name.startswith("whois"):
                result["osint"]["whois"] = content
            elif lower_name.startswith("asn"):
                result["osint"]["asn"] = content
            elif "reverse_ip" in lower_name:
                result["osint"]["reverse_ip"] = content
            elif "s3" in lower_name:
                result["osint"]["s3_buckets"] = content
            elif "dork" in lower_name:
                result["osint"]["github_dorks"] = content
            elif "social" in lower_name:
                result["osint"]["social"] = content

            # Vulnerabilities & Findings
            if "finding" in lower_name or "vuln" in lower_name or "nuclei" in lower_name:
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            findings_list.append(_normalize_finding(item, target_name))
                elif isinstance(content, dict):
                    if "findings" in content and isinstance(content["findings"], list):
                        for item in content["findings"]:
                            if isinstance(item, dict):
                                findings_list.append(_normalize_finding(item, target_name))
                elif isinstance(content, str):
                    for line in content.splitlines():
                        if any(sev in line.upper() for sev in ("[CRITICAL]", "[HIGH]", "[MEDIUM]", "[LOW]")):
                            findings_list.append(_parse_text_finding(line, target_name))

            # Dalfox XSS findings
            if "dalfox" in lower_name and isinstance(content, str):
                for line in content.splitlines():
                    if "[POC]" in line.upper() or "[V]" in line.upper():
                        findings_list.append({
                            "title": "Cross-Site Scripting (XSS) via Dalfox",
                            "severity": "HIGH",
                            "target": target_name,
                            "category": "Injection",
                            "poc": line.strip(),
                            "remediation": "Sanitize and contextually encode all dynamic user inputs before rendering in the DOM."
                        })

    # Add target host to subdomains if empty
    if not subdomains_set and target_name and target_name != "unknown":
        subdomains_set.add(target_name)

    result["subdomains"] = sorted(list(subdomains_set))
    result["urls"] = sorted(list(urls_set))
    result["emails"] = sorted(list(emails_set))
    result["findings"] = findings_list

    # Compute Statistics & Risk Score
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings_list:
        sev = str(f.get("severity", "info")).lower()
        if sev in severity_counts:
            severity_counts[sev] += 1
        else:
            severity_counts["info"] += 1

    total_findings = sum(severity_counts.values())

    # Risk level calculation
    if severity_counts["critical"] > 0:
        risk_level = "CRITICAL"
        risk_score = 95
    elif severity_counts["high"] > 0:
        risk_level = "HIGH"
        risk_score = 80
    elif severity_counts["medium"] > 0:
        risk_level = "MEDIUM"
        risk_score = 55
    elif severity_counts["low"] > 0:
        risk_level = "LOW"
        risk_score = 30
    elif len(subdomains_set) > 0 or len(urls_set) > 0:
        risk_level = "SECURE"
        risk_score = 15
    else:
        risk_level = "INFORMATIONAL"
        risk_score = 10

    result["stats"] = {
        "subdomains_count": len(subdomains_set),
        "urls_count": len(urls_set),
        "ports_count": len(result["ports"]),
        "emails_count": len(emails_set),
        "artifacts_count": artifacts_count,
        "findings_count": severity_counts,
        "total_findings": total_findings,
    }
    result["risk_level"] = risk_level
    result["risk_score"] = risk_score

    log.success(f"Collected {len(result['modules'])} result file(s), {len(subdomains_set)} subdomains, {total_findings} findings from {output_dir}")
    return result


def _normalize_finding(item: dict, default_target: str) -> dict:
    """Normalize a raw JSON finding dictionary into standard schema."""
    sev = str(item.get("severity") or item.get("info", {}).get("severity") or "INFO").upper()
    title = item.get("name") or item.get("title") or item.get("info", {}).get("name") or "Security Finding"
    category = item.get("category") or item.get("type") or item.get("info", {}).get("tags") or "Vulnerability"
    if isinstance(category, list):
        category = ", ".join(category)
    poc = item.get("poc") or item.get("matched_at") or item.get("matched") or item.get("url") or ""
    remediation = item.get("remediation") or item.get("info", {}).get("remediation") or "Apply vendor patches and validate input boundaries."

    return {
        "title": title,
        "severity": sev if sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO") else "INFO",
        "target": item.get("target") or item.get("host") or default_target,
        "category": str(category),
        "poc": str(poc),
        "remediation": str(remediation),
        "description": item.get("description") or item.get("info", {}).get("description") or ""
    }


def _parse_text_finding(line: str, default_target: str) -> dict:
    """Extract finding from text lines."""
    sev = "INFO"
    for s in ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"):
        if f"[{s}]" in line.upper():
            sev = s
            break

    clean_title = re.sub(r"\[(CRITICAL|HIGH|MEDIUM|LOW|INFO)\]", "", line, flags=re.IGNORECASE).strip()
    return {
        "title": clean_title[:80] or "Vulnerability Finding",
        "severity": sev,
        "target": default_target,
        "category": "Recon/Vulnerability",
        "poc": line.strip(),
        "remediation": "Review system configuration and update affected software versions.",
        "description": line.strip()
    }

