from flask import Blueprint, jsonify, current_app
import os

try:
    import requests
except ImportError:
    requests = None

try:
    from azure.identity import DefaultAzureCredential
except Exception:
    DefaultAzureCredential = None

bp = Blueprint("openai", __name__, url_prefix="/health")

@bp.route("/openai", methods=["GET"])
def openai_check():
    """
    Checks OpenAI or Azure OpenAI connectivity.
    Supports:
    - API key (OPENAI_API_KEY)
    - Managed Identity / Service Principal (DefaultAzureCredential)
    """
    current_app.logger.info("Health openai check requested")

    if requests is None:
        return jsonify({"openai": "error", "message": "requests not installed"}), 503

    # API key mode
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")

    if api_key:
        url = (base_url or "https://api.openai.com").rstrip("/") + "/v1/models"
        try:
            resp = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=3)
            if resp.status_code == 200:
                return jsonify({"openai": "ok", "auth_mode": "api_key"}), 200
            elif resp.status_code in (401, 403):
                return jsonify({"openai": "unauthorized", "auth_mode": "api_key"}), 503
            return jsonify({"openai": "error", "status_code": resp.status_code}), 503
        except Exception:
            current_app.logger.exception("OpenAI API key mode check failed")
            return jsonify({"openai": "unavailable", "auth_mode": "api_key"}), 503

    # Azure OpenAI managed identity mode
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if endpoint and DefaultAzureCredential:
        try:
            cred = DefaultAzureCredential()
            token = cred.get_token("https://cognitiveservices.azure.com/.default")
            headers = {"Authorization": f"Bearer {token.token}"}
            url = endpoint.rstrip("/") + "/openai/deployments?api-version=2023-05-15"
            resp = requests.get(url, headers=headers, timeout=3)
            if resp.status_code == 200:
                return jsonify({"openai": "ok", "auth_mode": "managed_identity"}), 200
            elif resp.status_code in (401, 403):
                return jsonify({"openai": "unauthorized", "auth_mode": "managed_identity"}), 503
            return jsonify({"openai": "error", "status_code": resp.status_code}), 503
        except Exception:
            current_app.logger.exception("Azure OpenAI managed identity check failed")
            return jsonify({"openai": "unavailable", "auth_mode": "managed_identity"}), 503

    return jsonify({"openai": "error", "message": "No API key or Azure Managed Identity setup found"}), 503
