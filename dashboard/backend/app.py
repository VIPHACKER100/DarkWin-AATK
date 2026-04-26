"""
DARKWIN — Dashboard Backend
Flask REST API with SocketIO real-time log streaming.

⚠  Confirm authentication requirements with product owner before deploying.
"""

import os
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, send_file, abort
from flask_socketio import SocketIO
from flask_cors import CORS


def create_app(reports_dir: str = "reports", logs_dir: str = "logs"):
    """
    Create and configure the Flask application and SocketIO instance.

    Args:
        reports_dir: Path to the scan reports directory.
        logs_dir:    Path to the session logs directory.

    Returns:
        Tuple of (Flask app, SocketIO instance).
    """
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("DARKWIN_SECRET", "darkwin-dev-secret")
    CORS(app, origins="*")
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

    # ── REST Endpoints ──────────────────────────────────────────────────────

    @app.route("/targets", methods=["GET"])
    def list_targets():
        """Return list of all scan output directories."""
        base = Path(reports_dir)
        if not base.exists():
            return jsonify([])
        targets = [
            {
                "target": d.name,
                "sessions": [s.name for s in sorted(d.iterdir()) if s.is_dir()],
            }
            for d in sorted(base.iterdir())
            if d.is_dir()
        ]
        return jsonify(targets)

    @app.route("/report/<target>/<session>", methods=["GET"])
    def get_report(target: str, session: str):
        """Return the HTML report for a specific target/session."""
        report_path = Path(reports_dir) / target / session / "report.html"
        if not report_path.exists():
            abort(404, description=f"Report not found: {report_path}")
        return send_file(str(report_path), mimetype="text/html")

    @app.route("/status/<scan_id>", methods=["GET"])
    def get_status(scan_id: str):
        """Return the last 100 lines of the log file for a scan session."""
        log_path = Path(logs_dir) / f"{scan_id}.log"
        if not log_path.exists():
            return jsonify({"error": "Log not found", "scan_id": scan_id}), 404

        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return jsonify({"scan_id": scan_id, "lines": lines[-100:]})

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok", "service": "DARKWIN Dashboard"})

    # ── SocketIO — Live log streaming ───────────────────────────────────────

    @socketio.on("subscribe")
    def handle_subscribe(data):
        """Client subscribes to real-time updates for a scan session log."""
        scan_id = data.get("scan_id", "")
        log_path = Path(logs_dir) / f"{scan_id}.log"

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
