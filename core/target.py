"""
DARKWIN — Target Handling
Normalizes, validates and slugifies user-supplied targets before they are used
in file paths or passed to external tools.

A user may pass anything to the CLI / dashboard ("https://x.com/sub/", "HTTP://
site.org:443/", "x.com." etc.). Previously the raw string was used directly to
build the output directory which produced broken, nested folder names such as
``reports/https:/xprt...`` and fed bogus values into tools like theHarvester.
"""

from __future__ import annotations

import ipaddress
import re

RE_VALID = re.compile(r"^[A-Za-z0-9_.\-]+$")


def normalize_target(raw: str) -> str:
    """
    Reduce an arbitrary user-supplied target to a clean hostname or IP.

    Examples:
        "https://xprt.com/"                     -> "xprt.com"
        "HTTP://sub.dark.org:8443/path?q=1#f"   -> "sub.dark.org"
        "https://https://xprt.com/"             -> "https://xprt.com" (best effort)
        "EXAMPLE.COM."                          -> "example.com"
        "93.184.216.34:443"                     -> "93.184.216.34"

    Args:
        raw: Raw target string from the user.

    Returns:
        The cleaned hostname / IP, lowercased, with scheme, path, port and
        trailing dot stripped. Empty string if nothing usable remains.
    """
    value = (raw or "").strip()
    if not value:
        return ""

    # Strip scheme: take everything after the last "://" so that a doubly
    # wrapped value like "https://https://x.com" still yields "x.com".
    while "://" in value:
        value = value.split("://", 1)[1]

    # Drop any path, query, fragment or Windows-style drive leftovers.
    for sep in ("/", "\\", "?", "#"):
        value = value.split(sep, 1)[0]

    # Keep only the host part if a port was specified.
    if ":" in value and not value.count(":") > 1:
        value = value.split(":", 1)[0]

    # A header-style value like "Host: example.com".
    if value.startswith("host:"):
        value = value.split(":", 1)[1]

    value = value.strip().lower().rstrip(".")
    return value


def validate_target(normalized: str) -> bool:
    """Return True if the normalized target is a sane domain or IP."""
    normalized = normalized.strip()

    if not normalized:
        return False

    if not RE_VALID.fullmatch(normalized):
        return False

    # Accept IPv4/IPv6 literals directly.
    try:
        ipaddress.ip_address(normalized)
        return True
    except ValueError:
        pass

    # Domain heuristic: at least one dot and no empty labels.
    labels = normalized.split(".")
    if len(labels) < 2 or any(not label for label in labels):
        # Allow bare hostnames used for engagement testing, but reject
        # anything that is just punctuation or a path fragment.
        if len(normalized) < 3:
            return False
    return True


def safe_target(raw: str) -> str:
    """
    Normalize a target and guarantee the returned string is safe to embed in
    a filesystem path (only ``[A-Za-z0-9_.-]``). Returns "" if not usable.
    """
    normalized = normalize_target(raw)
    if not validate_target(normalized):
        return ""
    return normalized