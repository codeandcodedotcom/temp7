from flask import Blueprint, jsonify, current_app

bp = Blueprint("hello", __name__, url_prefix="/health")

@bp.route("/hello", methods=["GET"])
def hello():
    """
    Basic hello route — useful for environment identification.
    """
    current_app.logger.info("Health hello check")
    return jsonify({
        "message": "hello",
        "service": current_app.config.get("SERVICE_NAME"),
        "env": current_app.config.get("ENVIRONMENT"),
        "version": current_app.config.get("SERVICE_VERSION")
    }), 200
