import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from azure.identity import ClientSecretCredential
except Exception:
    ClientSecretCredential = None


def check_postgres_sp(timeout: int = 3):
    """
    Postgres connectivity check.
    """

    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed")

    if ClientSecretCredential is None:
        raise RuntimeError("azure-identity ClientSecretCredential not available; please install azure-identity")

    tenant = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    host = os.getenv("DATABASE_HOST")
    name = os.getenv("DATABASE_NAME")
    user = os.getenv("DATABASE_USER")

    missing = [n for n, v in (
        ("AZURE_TENANT_ID", tenant),
        ("AZURE_CLIENT_ID", client_id),
        ("AZURE_CLIENT_SECRET", client_secret),
        ("DATABASE_HOST", host),
        ("DATABASE_NAME", name),
        ("DATABASE_USER", user),
    ) if not v]

    if missing:
        raise ValueError(f"Missing environment variables required for SP DB auth: {', '.join(missing)}")

    resource = os.getenv("AZURE_RESOURCE", "https://ossrdbms-aad.database.windows.net")
    scope = resource.rstrip("/") + "/.default"

    cred = ClientSecretCredential(tenant_id=tenant, client_id=client_id, client_secret=client_secret)
    token = cred.get_token(scope)
    access_token = token.token  # short-lived bearer token

    conn = psycopg2.connect(
        host=host,
        dbname=name,
        user=user,
        password=access_token,
        sslmode="require",
        connect_timeout=timeout
    )

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        val = cur.fetchone()[0]
        cur.close()
        return {"db": "ok", "mode": "service_principal", "result": val}
    finally:
        conn.close()
