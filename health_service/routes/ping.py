from flask import Blueprint, jsonify, current_app
import time

bp = Blueprint("ping", __name__, url_prefix="/health")

@bp.route("/ping", methods=["GET"])
def ping():
    """
    Simple liveness check. Returns 200 if app is alive.
    """
    current_app.logger.info("Health ping OK")
    return jsonify({
        "status": "ok",
        "check": "ping",
        "time": int(time.time())
    }), 200
