from flask import Blueprint, jsonify, current_app
import os

try:
    import requests
except Exception:
    requests = None

try:
    from azure.identity import ClientSecretCredential
except Exception:
    ClientSecretCredential = None

bp = Blueprint("openai", __name__, url_prefix="/health")


@bp.route("/openai", methods=["GET"])
def openai_check():
    """
    Health-check for Azure OpenAI using a Service Principal (Client Secret).
    Required env vars:
      - AZURE_TENANT_ID
      - AZURE_CLIENT_ID
      - AZURE_CLIENT_SECRET
      - AZURE_OPENAI_ENDPOINT (e.g. https://<resource>.openai.azure.com/)
    """
    current_app.logger.info("Health openai check requested (service-principal mode)")

    if requests is None:
        current_app.logger.error("requests library not installed")
        return jsonify({"openai": "error", "message": "requests library not installed"}), 503

    if ClientSecretCredential is None:
        current_app.logger.error("azure-identity.ClientSecretCredential not available")
        return jsonify({"openai": "error", "message": "azure-identity library not installed"}), 503

    tenant = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

    missing = [name for name, val in (
        ("AZURE_TENANT_ID", tenant),
        ("AZURE_CLIENT_ID", client_id),
        ("AZURE_CLIENT_SECRET", client_secret),
        ("AZURE_OPENAI_ENDPOINT", endpoint),
    ) if not val]

    if missing:
        msg = f"missing env: {', '.join(missing)}"
        current_app.logger.warning("OpenAI health check misconfigured: %s", msg)
        return jsonify({"openai": "error", "message": msg}), 503

    try:
        # authenticate with Service Principal
        cred = ClientSecretCredential(tenant_id=tenant, client_id=client_id, client_secret=client_secret)
        token = cred.get_token("https://cognitiveservices.azure.com/.default")
        headers = {"Authorization": f"Bearer {token.token}"}

        url = endpoint.rstrip("/") + "/openai/deployments?api-version=2023-05-15"
        resp = requests.get(url, headers=headers, timeout=3)

        if resp.status_code == 200:
            return jsonify({"openai": "ok", "auth_mode": "service_principal"}), 200
        if resp.status_code in (401, 403):
            current_app.logger.warning("OpenAI unauthorized (status=%s)", resp.status_code)
            return jsonify({"openai": "unauthorized", "auth_mode": "service_principal"}), 503

        current_app.logger.warning("OpenAI unexpected status %s", resp.status_code)
        return jsonify({"openai": "error", "status_code": resp.status_code}), 503

    except Exception:
        current_app.logger.exception("Azure OpenAI service-principal check failed")
        return jsonify({"openai": "unavailable", "auth_mode": "service_principal"}), 503
