"""
DARKWIN — Unit Tests | Target Normalization
"""

from core.target import normalize_target, safe_target, validate_target


def test_strips_scheme():
    assert normalize_target("https://example.com") == "example.com"
    assert normalize_target("HTTP://example.com/") == "example.com"
    assert normalize_target("ftp://example.com") == "example.com"


def test_strips_scheme_path_and_query():
    assert normalize_target("https://example.com/about.aspx?id=1#frag") == "example.com"
    assert normalize_target("http://testaspnet.vulnweb.com/about.aspx") == "testaspnet.vulnweb.com"


def test_strips_port_and_trailing_dot():
    assert normalize_target("example.com:8443") == "example.com"
    assert normalize_target("EXAMPLE.COM.") == "example.com"


def test_double_scheme_best_effort():
    assert normalize_target("https://https://xprtcommunity.in/") == "xprtcommunity.in"


def test_ip_literal_untouched():
    assert normalize_target("93.184.216.34") == "93.184.216.34"
    assert normalize_target("2606:4700::6815:1ede") == "2606:4700::6815:1ede"


def test_empty_and_garbage():
    assert normalize_target("") == ""
    assert normalize_target("   ") == ""
    assert normalize_target("https://") == ""


def test_validate():
    assert validate_target("example.com") is True
    assert validate_target("93.184.216.34") is True
    assert validate_target("sub.example.co.uk") is True
    assert validate_target("https://example.com") is False
    assert validate_target("../etc/passwd") is False
    assert validate_target("") is False


def test_safe_target_rejects_urls():
    # The exact bug that created reports/https:/... folders.
    assert safe_target("http://testaspnet.vulnweb.com/about.aspx") == "testaspnet.vulnweb.com"
    assert safe_target("https://https://xprtcommunity.in/") == "xprtcommunity.in"