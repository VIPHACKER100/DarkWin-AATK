"""
DARKWIN — Unit Tests | OSINT Helpers (Breach Lookup)
"""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_hibp_api_base_url():
    from modules.osint.breach_lookup import HIBP_API_BASE
    assert "haveibeenpwned.com" in HIBP_API_BASE
    assert "api/v3" in HIBP_API_BASE


@patch("modules.osint.breach_lookup.requests.get")
def test_query_hibp_returns_json_on_200(mock_get):
    from modules.osint.breach_lookup import _query_hibp
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"Name": "Adobe"}]
    mock_get.return_value = mock_resp

    result = _query_hibp("https://haveibeenpwned.com/api/v3/breachedaccount/test@test.com", "key", MagicMock())
    assert result == [{"Name": "Adobe"}]


@patch("modules.osint.breach_lookup.requests.get")
def test_query_hibp_returns_empty_list_on_404(mock_get):
    from modules.osint.breach_lookup import _query_hibp
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    result = _query_hibp("https://test.com", "key", MagicMock())
    assert result == []


@patch("modules.osint.breach_lookup.requests.get")
def test_query_hibp_returns_none_on_500(mock_get):
    from modules.osint.breach_lookup import _query_hibp
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_get.return_value = mock_resp

    mock_log = MagicMock()
    result = _query_hibp("https://test.com", "key", mock_log)
    assert result is None
    mock_log.error.assert_called()


@patch("modules.osint.breach_lookup.requests.get")
def test_query_hibp_returns_none_on_network_error(mock_get):
    from modules.osint.breach_lookup import _query_hibp
    import requests
    mock_get.side_effect = requests.RequestException("timeout")

    mock_log = MagicMock()
    result = _query_hibp("https://test.com", "key", mock_log)
    assert result is None
    mock_log.error.assert_called()


@patch("modules.osint.breach_lookup.requests.get")
def test_query_hibp_rate_limit_warning(mock_get):
    from modules.osint.breach_lookup import _query_hibp
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_get.return_value = mock_resp

    mock_log = MagicMock()
    result = _query_hibp("https://test.com", "key", mock_log)
    assert result is None
    mock_log.warning.assert_called()
