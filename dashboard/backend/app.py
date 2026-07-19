import os
import re
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, request, abort
from flask_socketio import SocketIO
from flask_cors import CORS

_current_scan = {"scan_id": None, "target": None, "mode": None, "status": "idle", "started_at": None, "phase": None}
_scan_history = []

def create_app(reports_dir: str = "reports", logs_dir: str = "logs"):
    global _current_scan, _scan_history

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("DARKWIN_SECRET", "darkwin-dev-secret")
    CORS(app, origins="*")
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    logs_base = Path(logs_dir).resolve()
    reports_base = Path(reports_dir).resolve()

    def _safe_log_path(scan_id: str) -> Path:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", scan_id):
            abort(400, description="Invalid scan_id")
        candidate = (logs_base / f"{scan_id}.log").resolve()
        if logs_base not in candidate.parents:
            abort(400, description="Invalid scan_id")
        return candidate

    @app.route("/targets", methods=["GET"])
    def list_targets():
        base = Path(reports_dir)
        if not base.exists():
            return jsonify([])
        targets = [
            {
                "target": d.name,
                "sessions": sorted([s.name for s in d.iterdir() if s.is_dir()], reverse=True),
            }
            for d in sorted(base.iterdir()) if d.is_dir()
        ]
        return jsonify(targets)

    @app.route("/report/<target>/<session>", methods=["GET"])
    def get_report(target: str, session: str):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", target):
            abort(400, description="Invalid target")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", session):
            abort(400, description="Invalid session")
        relative_report = f"{target}/{session}/report.html"
        report_path = (reports_base / relative_report).resolve()
        try:
            report_path.relative_to(reports_base)
        except ValueError:
            abort(400, description="Invalid report path")
        if not report_path.exists():
            abort(404, description="Report not found")
        return send_from_directory(str(reports_base), relative_report, mimetype="text/html")

    @app.route("/status/<scan_id>", methods=["GET"])
    def get_status(scan_id: str):
        log_path = _safe_log_path(scan_id)
        if not log_path.exists():
            return jsonify({"error": "Log not found", "scan_id": scan_id}), 404
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return jsonify({"scan_id": scan_id, "lines": lines[-100:]})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "DARKWIN Dashboard", "timestamp": datetime.now(timezone.utc).isoformat()})

    @app.route("/tools", methods=["GET"])
    def check_tools():
        import shutil
        from core.config_loader import load_config
        cfg = load_config()
        tools = cfg.get("tools", {})
        results = {}
        for name, binary in tools.items():
            results[name] = shutil.which(binary) is not None
        return jsonify(results)

    @app.route("/scan", methods=["POST"])
    def start_scan():
        data = request.get_json(force=True)
        target = data.get("target", "").strip()
        mode = data.get("mode", "recon").strip().lower()

        if not target:
            return jsonify({"error": "target is required"}), 400
        if mode not in ("recon", "scan", "bounty"):
            return jsonify({"error": "mode must be recon, scan, or bounty"}), 400
        if _current_scan["status"] == "running":
            return jsonify({"error": "A scan is already running", "current": _current_scan}), 409

        scan_id = f"{target.replace('.', '_')}_{int(time.time())}"
        _current_scan.update(scan_id=scan_id, target=target, mode=mode, status="running", started_at=datetime.now(timezone.utc).isoformat(), phase="initializing")
        _scan_history.insert(0, dict(_current_scan))

        def _run():
            try:
                from core.logger import setup_logger
                from core.pipeline import run_pipeline
                log_dir = logs_dir
                setup_logger(log_dir=log_dir, tool_name="darkwin", target=target)

                phases = {"recon": ["subdomains", "httpx", "gau", "katana", "nuclei"], "scan": ["recon", "port-scan", "web-scan", "dalfox", "nuclei"], "bounty": ["recon", "port-scan", "web-scan", "dalfox", "nuclei", "gowitness"]}
                for phase in phases.get(mode, ["running"]):
                    if _current_scan["status"] != "running":
                        break
                    _current_scan["phase"] = phase
                    socketio.emit("scan_phase", {"scan_id": scan_id, "phase": phase, "mode": mode})
                    time.sleep(0.5)
                    run_pipeline(mode, target)

                _current_scan["status"] = "completed"
                _current_scan["phase"] = "done"
                socketio.emit("scan_done", {"scan_id": scan_id, "target": target, "mode": mode})
            except Exception as e:
                _current_scan["status"] = "failed"
                _current_scan["phase"] = f"error: {e}"
                socketio.emit("scan_error", {"scan_id": scan_id, "error": str(e)})
            finally:
                if _scan_history:
                    _scan_history[0] = dict(_current_scan)

        threading.Thread(target=_run, daemon=True).start()
        return jsonify({"scan_id": scan_id, "target": target, "mode": mode, "status": "started"}), 202

    @app.route("/scan/current", methods=["GET"])
    def current_scan():
        return jsonify(_current_scan)

    @app.route("/scan/history", methods=["GET"])
    def scan_history():
        return jsonify(_scan_history[:20])

    @socketio.on("connect")
    def handle_connect():
        pass

    @socketio.on("subscribe")
    def handle_subscribe(data):
        scan_id = data.get("scan_id", "")
        try:
            log_path = _safe_log_path(scan_id)
        except Exception:
            return

        def tail_log():
            pos = 0
            while True:
                if log_path.exists():
                    with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                        f.seek(pos)
                        new_lines = f.readlines()
                        pos = f.tell()
                    for line in new_lines:
                        socketio.emit("scan_update", {"scan_id": scan_id, "line": line.rstrip()})
                time.sleep(1)

        thread = threading.Thread(target=tail_log, daemon=True)
        thread.start()

    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
