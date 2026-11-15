"""Marswalk Surface Explorer - Flask backend.

Run locally:   python app.py
Production:    gunicorn "app:create_app()"
"""

from __future__ import annotations

import logging
import os
import time

from flask import Flask, jsonify, render_template, request

from imagery import ImageryService
from mission_data import MISSION, REFERENCE_TELEMETRY
from planning import analyse_route

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger("marswalk")

STARTED_AT = time.time()


def build_mission_payload() -> dict:
    """Mission definition plus computed route analysis."""
    return {
        **MISSION,
        "route_analysis": analyse_route(MISSION),
        "reference_telemetry": REFERENCE_TELEMETRY,
    }


def create_app(imagery: ImageryService | None = None) -> Flask:
    app = Flask(__name__)
    imagery = imagery or ImageryService(
        ttl_seconds=int(os.environ.get("IMAGERY_TTL_SECONDS", "3600"))
    )

    @app.after_request
    def security_headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        return resp

    @app.get("/")
    def index():
        # Imagery is loaded by the browser after first paint, so a slow
        # NASA response can never block the page.
        return render_template("index.html", mission=build_mission_payload())

    @app.get("/api/v1/mission")
    def api_mission():
        return jsonify(build_mission_payload())

    @app.get("/api/v1/imagery")
    def api_imagery():
        return jsonify(imagery.get())

    @app.get("/api/v1/status")
    def api_status():
        """Honest service health - not a simulated link to anything."""
        return jsonify(
            {
                "status": "ok",
                "uptime_s": round(time.time() - STARTED_AT),
                "imagery_cached": imagery.has_cache,
            }
        )

    @app.errorhandler(404)
    def not_found(_):
        if request.path.startswith("/api/"):
            return jsonify({"error": "not_found"}), 404
        return render_template("index.html", mission=build_mission_payload()), 404

    @app.errorhandler(500)
    def server_error(exc):
        logger.exception("Unhandled error: %s", exc)
        return jsonify({"error": "internal_server_error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
