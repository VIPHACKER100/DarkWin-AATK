"""
DARKWIN — Integration Tests | Dashboard (Extended Coverage)
"""

import pytest
import time
import threading
from pathlib import Path
from unittest.mock import patch, MagicMock


@pytest.fixture
def client(tmp_path):
    from dashboard.backend.app import create_app
    import dashboard.backend.app as app_mod

    reports_dir = tmp_path / "reports"
    logs_dir = tmp_path / "logs"
    reports_dir.mkdir()
    logs_dir.mkdir()

    # Reset global state
    app_mod._current_scan = {"scan_id": None, "target": None, "mode": None, "status": "idle", "started_at": None, "phase": None}
    app_mod._scan_history = []

    with patch("core.config_loader.load_config") as mock_config:
        mock_config.return_value = {"tools": {"nmap": "nmap", "ls": "ls"}}
        app, socketio = create_app(reports_dir=str(reports_dir), logs_dir=str(logs_dir))
        app.config["TESTING"] = True
        with app.test_client() as c:
            yield c, reports_dir, logs_dir, app_mod


def test_tools_route(client):
    c, _, _, _ = client
    with patch("core.config_loader.load_config") as mock_config:
        mock_config.return_value = {"tools": {"nmap": "nmap", "ls": "ls"}}
        resp = c.get("/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "nmap" in data
        assert "ls" in data


def test_tools_route_empty(client):
    c, _, _, _ = client
    with patch("core.config_loader.load_config") as mock_config:
        mock_config.return_value = {"tools": {}}
        resp = c.get("/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {}


def test_start_scan_already_running(client):
    c, _, _, app_mod = client
    app_mod._current_scan["status"] = "running"

    resp = c.post("/scan", json={"target": "example.com", "mode": "recon"})
    assert resp.status_code == 409
    data = resp.get_json()
    assert "already running" in data["error"]


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
def test_start_scan_records_history(mock_logger, mock_pipeline, client):
    c, _, _, app_mod = client
    resp = c.post("/scan", json={"target": "example.com", "mode": "recon"})
    assert resp.status_code == 202

    time.sleep(0.1)
    assert len(app_mod._scan_history) >= 1
    assert app_mod._scan_history[0]["target"] == "example.com"


@patch("core.pipeline.run_pipeline")
@patch("core.logger.setup_logger")
def test_start_scan_default_mode(mock_logger, mock_pipeline, client):
    c, _, _, _ = client
    resp = c.post("/scan", json={"target": "example.com"})
    assert resp.status_code == 202
    data = resp.get_json()
    assert data["mode"] == "recon"


def test_safe_log_path_valid(client):
    c, _, logs_dir, _ = client
    log_file = logs_dir / "valid_scan_123.log"
    log_file.write_text("test log\n")

    resp = c.get("/status/valid_scan_123")
    assert resp.status_code == 200


def test_safe_log_path_traversal(client):
    c, _, _, _ = client
    resp = c.get("/status/..%2F..%2Fetc%2Fpasswd")
    assert resp.status_code in (400, 404)


def test_report_path_traversal(client):
    c, _, _, _ = client
    resp = c.get("/report/..%2F..%2Fetc/passwd/2025-01-01")
    assert resp.status_code in (400, 404)


def test_status_returns_last_100_lines(client):
    c, _, logs_dir, _ = client
    lines = "\n".join([f"line {i}" for i in range(150)])
    (logs_dir / "big_scan.log").write_text(lines)

    resp = c.get("/status/big_scan")
    assert resp.status_code == 200
    data = resp.get_json()
    assert len(data["lines"]) == 100
    assert data["lines"][-1] == "line 149"


def test_targets_multiple(client):
    c, reports_dir, _, _ = client
    for t in ["a.com", "b.com", "c.com"]:
        (reports_dir / t / "session1").mkdir(parents=True)

    resp = c.get("/targets")
    data = resp.get_json()
    assert len(data) == 3
    target_names = {d["target"] for d in data}
    assert target_names == {"a.com", "b.com", "c.com"}
