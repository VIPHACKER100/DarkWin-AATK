"""
DARKWIN — Recon | S3 Bucket Scanner
Discovers publicly accessible S3 buckets by permuting the target domain name.
"""

import requests
import itertools
from pathlib import Path
from core.logger import get_logger

PERMUTATION_PREFIXES = [
    "", "dev-", "staging-", "prod-", "backup-", "data-",
    "assets-", "static-", "media-", "files-", "logs-",
    "admin-", "api-", "internal-", "public-", "private-",
    "cdn-", "images-", "uploads-",
]

PERMUTATION_SUFFIXES = [
    "", "-dev", "-staging", "-prod", "-backup", "-data",
    "-assets", "-static", "-media", "-files", "-logs",
    "-admin", "-api", "-internal", "-public",
]

S3_ENDPOINTS = [
    "https://{bucket}.s3.amazonaws.com",
    "https://s3.amazonaws.com/{bucket}",
    "https://{bucket}.s3.us-east-1.amazonaws.com",
]


def run(target: str, output_dir: str) -> None:
    """
    Generate S3 bucket name permutations and check for public access.

    Args:
        target:     Target domain name used to generate bucket name candidates.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="s3_bucket_scan", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    domain_base = target.replace(".", "-").lower()
    buckets = _generate_bucket_names(domain_base)
    log.info(f"Testing {len(buckets)} S3 bucket permutations for: {target}")

    out_file = f"{output_dir}/s3_buckets.txt"
    open_count = 0

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# S3 Bucket Scan — {target}\n\n")
        f.write("## Open/Accessible Buckets\n\n")

        for bucket in buckets:
            for endpoint_template in S3_ENDPOINTS:
                url = endpoint_template.format(bucket=bucket)
                status = _check_bucket(url)

                if status in (200, 403):
                    label = "OPEN (200)" if status == 200 else "FORBIDDEN (403 — exists)"
                    line = f"[{label}] {url}"
                    f.write(line + "\n")
                    log.warning(f"Bucket found: {line}")
                    open_count += 1
                    break  # No need to test other endpoint templates for same bucket name

    log.success(f"S3 scan complete. {open_count} bucket(s) found → {out_file}")


def _generate_bucket_names(base: str) -> list:
    """Generate a list of bucket name permutations from a base domain string."""
    names = set()
    for prefix in PERMUTATION_PREFIXES:
        for suffix in PERMUTATION_SUFFIXES:
            names.add(f"{prefix}{base}{suffix}")
    return list(names)


def _check_bucket(url: str) -> int:
    """Return the HTTP status code for a bucket URL, or 0 on connection error."""
    try:
        resp = requests.head(url, timeout=5, allow_redirects=True)
        return resp.status_code
    except requests.RequestException:
        return 0
