from flask import Blueprint, jsonify, request, current_app

bp = Blueprint("post", __name__, url_prefix="/health")

@bp.route("/post", methods=["POST"])
def post_check():
    """
    Accepts JSON and echoes it back. Useful to test POST handling.
    """
    current_app.logger.info("Health POST request received")
    payload = request.get_json(force=True, silent=True)
    return jsonify({"received": payload}), 200
