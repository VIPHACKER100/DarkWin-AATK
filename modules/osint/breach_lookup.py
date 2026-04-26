"""
DARKWIN — OSINT | Breach Lookup
Queries the HaveIBeenPwned API v3 to check if an email address has been compromised.

NOTE: Requires a HIBP API key in core/config.yaml under api_keys.hibp_api_key
"""

import json
import requests
from pathlib import Path
from core.logger import get_logger
from core.config_loader import load_config

HIBP_API_BASE = "https://haveibeenpwned.com/api/v3"


def run(email: str, output_dir: str) -> None:
    """
    Check an email address against the HaveIBeenPwned breach database.

    Args:
        email:      Email address to check (treated as the target identifier).
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="breach_lookup", target=email)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    config = load_config()
    api_key = config.get("api_keys", {}).get("hibp_api_key", "")

    if not api_key:
        log.error(
            "No HIBP API key configured. Add api_keys.hibp_api_key to core/config.yaml."
        )
        return

    out_file = f"{output_dir}/breach.json"
    log.info(f"Checking breach database for: {email}")

    # Check email in breaches
    breaches = _query_hibp(f"{HIBP_API_BASE}/breachedaccount/{email}", api_key, log)

    # Check email in pastes
    pastes = _query_hibp(f"{HIBP_API_BASE}/pasteaccount/{email}", api_key, log)

    result = {
        "email": email,
        "breaches": breaches or [],
        "pastes": pastes or [],
        "breach_count": len(breaches) if breaches else 0,
        "paste_count": len(pastes) if pastes else 0,
    }

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    if result["breach_count"] > 0:
        log.warning(
            f"⚠  {email} found in {result['breach_count']} breach(es) "
            f"and {result['paste_count']} paste(s) → {out_file}"
        )
    else:
        log.success(f"Email {email} not found in any known breaches → {out_file}")


def _query_hibp(url: str, api_key: str, log) -> list:
    """Send an authenticated HIBP API request and return JSON or None."""
    headers = {
        "hibp-api-key": api_key,
        "User-Agent": "DARKWIN-SecurityToolkit/1.0",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            return []
        elif resp.status_code == 429:
            log.warning("HIBP API rate limit reached. Please retry after 1 minute.")
        else:
            log.error(f"HIBP API error {resp.status_code} for {url}")
    except requests.RequestException as e:
        log.error(f"HIBP request failed: {e}")
    return None
