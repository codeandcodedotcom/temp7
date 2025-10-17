# utils/db_utils.py  (extract)
import os
import logging

try:
    import psycopg2
except Exception:
    psycopg2 = None

try:
    from azure.identity import ClientSecretCredential
except Exception:
    ClientSecretCredential = None


def check_postgres_sp(timeout: int = 3):
    """
    Connect to Azure Database for PostgreSQL using Service Principal (ClientSecretCredential).
    Required env vars:
      - AZURE_TENANT_ID
      - AZURE_CLIENT_ID
      - AZURE_CLIENT_SECRET
      - DATABASE_HOST      (e.g. mydb.postgres.database.azure.com)
      - DATABASE_NAME      (e.g. postgres)
      - DATABASE_USER      (the DB user / AAD mapped user to authenticate as)
    Optional:
      - AZURE_RESOURCE     (default: https://ossrdbms-aad.database.windows.net)
    Returns a dict (for JSONification by the route).
    """
    logger = logging.getLogger("db_utils")

    if psycopg2 is None:
        raise RuntimeError("psycopg2 is not installed")

    if ClientSecretCredential is None:
        raise RuntimeError("azure-identity ClientSecretCredential not available; install azure-identity")

    tenant = os.getenv("AZURE_TENANT_ID")
    client_id = os.getenv("AZURE_CLIENT_ID")
    client_secret = os.getenv("AZURE_CLIENT_SECRET")

    host = os.getenv("DATABASE_HOST")
    name = os.getenv("DATABASE_NAME", "postgres")
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

    # resource / scope for Azure DB tokens (default for Azure DB for Postgres)
    resource = os.getenv("AZURE_RESOURCE", "https://ossrdbms-aad.database.windows.net")
    scope = resource.rstrip("/") + "/.default"

    try:
        cred = ClientSecretCredential(tenant_id=tenant, client_id=client_id, client_secret=client_secret)
        token = cred.get_token(scope)
        access_token = token.token
    except Exception as ex:
        logger.exception("Failed to acquire AAD token for Postgres")
        return {"db": "unavailable", "error": "token_failure", "detail": str(ex)}

    # connect using token as password (Azure AD auth)
    try:
        conn = psycopg2.connect(
            host=host,
            dbname=name,
            user=user,
            password=access_token,
            sslmode="require",
            connect_timeout=timeout
        )
    except Exception as ex:
        logger.exception("Failed to open Postgres connection")
        return {"db": "unavailable", "error": "connect_failure", "detail": str(ex)}

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        val = cur.fetchone()[0]
        cur.close()
        return {"db": "ok", "mode": "service_principal", "result": val}
    except Exception as ex:
        logger.exception("Postgres query failed")
        return {"db": "unavailable", "error": "query_failure", "detail": str(ex)}
    finally:
        try:
            conn.close()
        except Exception:
            pass
