import os
import re
import shutil
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, send_from_directory, request, abort
from flask_socketio import SocketIO
from flask_cors import CORS

_current_scan = {"scan_id": None, "target": None, "mode": None, "status": "idle", "started_at": None, "phase": None}
_scan_history = []

def _err(msg, code=400):
    return jsonify({"error": msg, "code": code}), code

def _safe_path(base: Path, name: str, pattern: str) -> Path:
    if not re.fullmatch(pattern, name):
        abort(400, description=f"Invalid name: {name}")
    candidate = (base / name).resolve()
    if base not in candidate.parents:
        abort(400, description="Path traversal blocked")
    return candidate

RE_ID = r"[A-Za-z0-9_.-]+"

def create_app(reports_dir: str = None, logs_dir: str = None):
    global _current_scan, _scan_history

    reports_dir = reports_dir or os.environ.get("DARKWIN_REPORTS_DIR", "reports")
    logs_dir = logs_dir or os.environ.get("DARKWIN_LOGS_DIR", "logs")
    cors_origin = os.environ.get("DARKWIN_CORS_ORIGIN", "*")

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("DARKWIN_SECRET", "darkwin-dev-secret")
    CORS(app, origins=cors_origin)
    socketio = SocketIO(app, cors_allowed_origins=cors_origin, async_mode="threading")

    logs_base = Path(logs_dir).resolve()
    reports_base = Path(reports_dir).resolve()

    @app.route("/targets", methods=["GET"])
    def list_targets():
        base = Path(reports_dir)
        if not base.exists():
            return jsonify([])
        targets = []
        for d in sorted(base.iterdir()):
            if not d.is_dir():
                continue
            sessions = []
            for s in sorted(d.iterdir(), reverse=True):
                if s.is_dir():
                    report = s / "report.html"
                    sessions.append({
                        "name": s.name,
                        "hasReport": report.exists(),
                        "modified": datetime.fromtimestamp(s.stat().st_mtime, tz=timezone.utc).isoformat() if s.stat() else None,
                    })
            targets.append({"target": d.name, "sessions": sessions})
        return jsonify(targets)

    @app.route("/report/<target>/<session>", methods=["GET"])
    def get_report(target: str, session: str):
        tpath = _safe_path(reports_base, target, RE_ID)
        spath = _safe_path(tpath, session, RE_ID)
        report_path = spath / "report.html"
        if not report_path.exists():
            return _err("Report not found", 404)
        return send_from_directory(str(spath), "report.html", mimetype="text/html")

    @app.route("/status/<scan_id>", methods=["GET"])
    def get_status(scan_id: str):
        log_path = _safe_path(logs_base, f"{scan_id}.log", r"[A-Za-z0-9_.-]+\.log")
        if not log_path.exists():
            return _err("Log not found", 404)
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return jsonify({"scan_id": scan_id, "lines": lines[-100:]})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "DARKWIN Dashboard", "timestamp": datetime.now(timezone.utc).isoformat()})

    @app.route("/tools", methods=["GET"])
    def check_tools():
        from core.config_loader import load_config
        cfg = load_config()
        tools = cfg.get("tools", {})
        return jsonify({name: shutil.which(binary) is not None for name, binary in tools.items()})

    @app.route("/target/<target>", methods=["DELETE"])
    def delete_target(target: str):
        tpath = _safe_path(reports_base, target, RE_ID)
        if not tpath.exists():
            return _err("Target not found", 404)
        shutil.rmtree(tpath)
        socketio.emit("target_deleted", {"target": target})
        return jsonify({"deleted": target})

    @app.route("/target/<target>/<session>", methods=["DELETE"])
    def delete_session(target: str, session: str):
        tpath = _safe_path(reports_base, target, RE_ID)
        spath = _safe_path(tpath, session, RE_ID)
        if not spath.exists():
            return _err("Session not found", 404)
        shutil.rmtree(spath)
        socketio.emit("session_deleted", {"target": target, "session": session})
        return jsonify({"deleted": {"target": target, "session": session}})

    @app.route("/scan", methods=["POST"])
    def start_scan():
        data = request.get_json(force=True)
        target = (data.get("target") or "").strip()
        mode = (data.get("mode") or "recon").strip().lower()

        if not target:
            return _err("target is required")
        if mode not in ("recon", "scan", "bounty"):
            return _err("mode must be recon, scan, or bounty")
        if _current_scan["status"] == "running":
            return jsonify({"error": "A scan is already running", "current": _current_scan}), 409

        scan_id = f"{target.replace('.', '_')}_{int(time.time())}"
        _current_scan.update(scan_id=scan_id, target=target, mode=mode, status="running", started_at=datetime.now(timezone.utc).isoformat(), phase="initializing")
        _scan_history.insert(0, dict(_current_scan))

        phases = {"recon": ["recon_pipeline"], "scan": ["recon_pipeline", "full_scan_pipeline"], "bounty": ["recon_pipeline", "full_scan_pipeline", "bug_bounty_pipeline"]}

        def _run():
            try:
                from core.logger import setup_logger
                from core.pipeline import run_pipeline
                setup_logger(log_dir=logs_dir, tool_name="darkwin", target=target)

                for phase in phases.get(mode, ["pipeline"]):
                    if _current_scan["status"] != "running":
                        break
                    _current_scan["phase"] = phase
                    socketio.emit("scan_phase", {"scan_id": scan_id, "phase": phase, "mode": mode})
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

    @socketio.on("subscribe")
    def handle_subscribe(data):
        scan_id = data.get("scan_id", "")
        try:
            log_path = _safe_path(logs_base, f"{scan_id}.log", r"[A-Za-z0-9_.-]+\.log")
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

        threading.Thread(target=tail_log, daemon=True).start()

    return app, socketio

if __name__ == "__main__":
    app, socketio = create_app()
    port = int(os.environ.get("DARKWIN_PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
