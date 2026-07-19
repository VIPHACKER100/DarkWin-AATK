"""
DARKWIN — Integration Tests | Dashboard (Flask Routes)
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def client(tmp_path):
    from dashboard.backend.app import create_app

    reports_dir = tmp_path / "reports"
    logs_dir = tmp_path / "logs"
    reports_dir.mkdir()
    logs_dir.mkdir()

    with patch("core.config_loader.load_config") as mock_config:
        mock_config.return_value = {"tools": {"nmap": "nmap", "ls": "ls"}}
        app, socketio = create_app(reports_dir=str(reports_dir), logs_dir=str(logs_dir))
        app.config["TESTING"] = True
        with app.test_client() as client:
            yield client, reports_dir, logs_dir


def test_health_returns_200(client):
    c, _, _ = client
    resp = c.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "DARKWIN" in data["service"]
    assert "timestamp" in data


def test_targets_empty(client):
    c, reports_dir, _ = client
    resp = c.get("/targets")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_targets_with_data(client):
    c, reports_dir, _ = client
    target_dir = reports_dir / "example.com" / "2025-01-01"
    target_dir.mkdir(parents=True)

    resp = c.get("/targets")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["target"] == "example.com"
    assert any(s["name"] == "2025-01-01" for s in data[0]["sessions"])


def test_status_nonexistent_scan(client):
    c, _, _ = client
    resp = c.get("/status/nonexistent_scan_id")
    assert resp.status_code == 404


def test_status_valid_scan(client):
    c, _, logs_dir = client
    log_file = logs_dir / "test_scan_123.log"
    log_file.write_text("line1\nline2\nline3\n")

    resp = c.get("/status/test_scan_123")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["scan_id"] == "test_scan_123"
    assert len(data["lines"]) == 3


def test_status_invalid_scan_id(client):
    c, _, _ = client
    resp = c.get("/status/../../../etc/passwd")
    assert resp.status_code in (400, 404)


def test_report_nonexistent(client):
    c, _, _ = client
    resp = c.get("/report/example.com/2025-01-01")
    assert resp.status_code == 404


def test_report_valid(client):
    c, reports_dir, _ = client
    session_dir = reports_dir / "example.com" / "2025-01-01"
    session_dir.mkdir(parents=True)
    (session_dir / "report.html").write_text("<html>DARKWIN Report</html>")

    resp = c.get("/report/example.com/2025-01-01")
    assert resp.status_code == 200
    assert b"DARKWIN Report" in resp.data


def test_report_invalid_target(client):
    c, _, _ = client
    resp = c.get("/report/../../../etc/passwd/2025-01-01")
    assert resp.status_code in (400, 404)


def test_scan_current(client):
    c, _, _ = client
    resp = c.get("/scan/current")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data


def test_scan_history(client):
    c, _, _ = client
    resp = c.get("/scan/history")
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)


def test_start_scan_missing_target(client):
    c, _, _ = client
    resp = c.post("/scan", json={"mode": "recon"})
    assert resp.status_code == 400


def test_start_scan_invalid_mode(client):
    c, _, _ = client
    resp = c.post("/scan", json={"target": "example.com", "mode": "invalid"})
    assert resp.status_code == 400


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
def test_start_scan_valid(mock_logger, mock_pipeline, client):
    c, _, _ = client
    resp = c.post("/scan", json={"target": "example.com", "mode": "recon"})
    assert resp.status_code == 202
    data = resp.get_json()
    assert "scan_id" in data
    assert data["status"] == "started"
    assert data["target"] == "example.com"
