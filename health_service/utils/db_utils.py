import os

try:
    import psycopg2
except ImportError:
    psycopg2 = None

try:
    from azure.identity import DefaultAzureCredential
except ImportError:
    DefaultAzureCredential = None

def check_postgres_simple(timeout: int = 3):
    """
    Simple Postgres connectivity check.
    Modes:
      - Classic DSN (DATABASE_DSN)
      - Managed identity (AZURE_MANAGED=1 with DATABASE_HOST/NAME/USER)
    """
    if psycopg2 is None:
        raise RuntimeError("psycopg2 not installed")

    dsn = os.getenv("DATABASE_DSN")
    use_managed = os.getenv("AZURE_MANAGED", "0").lower() in ("1", "true", "yes")

    if dsn and not use_managed:
        conn = psycopg2.connect(dsn=dsn, connect_timeout=timeout)
        try:
            cur = conn.cursor()
            cur.execute("SELECT 1;")
            val = cur.fetchone()[0]
            cur.close()
            return {"db": "ok", "mode": "dsn", "result": val}
        finally:
            conn.close()

    if use_managed:
        if DefaultAzureCredential is None:
            raise RuntimeError("azure-identity not installed for managed identity mode")

        host = os.getenv("DATABASE_HOST")
        name = os.getenv("DATABASE_NAME")
        user = os.getenv("DATABASE_USER")
        if not all([host, name, user]):
            raise ValueError("DATABASE_HOST, DATABASE_NAME, DATABASE_USER required")

        cred = DefaultAzureCredential()
        resource = os.getenv("AZURE_RESOURCE", "https://ossrdbms-aad.database.windows.net")
        token = cred.get_token(resource + "/.default")
        access_token = token.token

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
            return {"db": "ok", "mode": "managed_identity", "result": val}
        finally:
            conn.close()

    raise RuntimeError("No DATABASE_DSN or managed identity configuration found")
