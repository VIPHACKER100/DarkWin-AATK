"""
DARKWIN — Recon | GitHub Dorking
Searches GitHub for sensitive information leaked about a target organisation.

NOTE: Requires a GitHub Personal Access Token in core/config.yaml under api_keys.github_token
"""

import requests
import json
from pathlib import Path
from core.logger import get_logger
from core.config_loader import load_config

DORK_PATTERNS = [
    "{target} password",
    "{target} secret",
    "{target} api_key",
    "{target} apikey",
    "{target} token",
    "{target} credentials",
    "{target} .env",
    "{target} config.yaml",
    "{target} private_key",
    "{target} BEGIN RSA",
    "{target} database_url",
    "{target} DB_PASSWORD",
    "{target} AWS_SECRET",
    "{target} GITHUB_TOKEN",
]


def run(target: str, output_dir: str) -> None:
    """
    Search GitHub for sensitive data leaks related to the target.

    Args:
        target:     Target organisation name or domain.
        output_dir: Directory to write results into.
    """
    log = get_logger(tool_name="github_dorking", target=target)
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    config = load_config()
    gh_token = config.get("api_keys", {}).get("github_token", "")

    if not gh_token:
        log.warning(
            "No GitHub token configured. Add api_keys.github_token to core/config.yaml. "
            "Saving dork URLs only."
        )

    out_file = f"{output_dir}/github_dorks.txt"
    results = []

    with open(out_file, "w", encoding="utf-8") as f:
        f.write(f"# GitHub Dorking Results — {target}\n\n")
        f.write("## Search URLs\n\n")

        for pattern in DORK_PATTERNS:
            query = pattern.format(target=target)
            url = f"https://github.com/search?q={requests.utils.quote(query)}&type=code"
            f.write(f"- {url}\n")

            if gh_token:
                api_result = _search_github_api(query, gh_token, log)
                results.extend(api_result)

        if results:
            f.write("\n## API Results\n\n")
            for r in results:
                f.write(f"### {r.get('name', 'unknown')}\n")
                f.write(f"- Repo: {r.get('repository', {}).get('full_name', 'N/A')}\n")
                f.write(f"- URL: {r.get('html_url', 'N/A')}\n\n")

    log.success(f"GitHub dorking complete → {out_file}")


def _search_github_api(query: str, token: str, log) -> list:
    """Query the GitHub Code Search API and return result items."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    params = {"q": query, "per_page": 10}

    try:
        resp = requests.get(
            "https://api.github.com/search/code",
            headers=headers,
            params=params,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("items", [])
        elif resp.status_code == 403:
            log.warning("GitHub API rate limit hit. Slow down requests.")
        else:
            log.warning(f"GitHub API returned {resp.status_code} for query: {query}")
    except requests.RequestException as e:
        log.error(f"GitHub API request failed: {e}")

    return []
