from flask import Blueprint, jsonify, current_app
from utils.db_utils import check_postgres_simple

bp = Blueprint("postgres", __name__, url_prefix="/health")

@bp.route("/postgres", methods=["GET"])
def postgres_check():
    """
    Tests PostgreSQL connectivity (supports DSN or Managed Identity).
    """
    current_app.logger.info("Health postgres check requested")
    try:
        result = check_postgres_simple()
        return jsonify(result), 200
    except Exception as e:
        current_app.logger.exception("Postgres health check failed")
        return jsonify({"db": "unavailable", "error": str(e)}), 503
