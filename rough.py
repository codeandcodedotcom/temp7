# Paste this single cell into a Databricks Python notebook and run.
# Replace TENANT_ID, CLIENT_ID, CLIENT_SECRET, and DATABRICKS_INSTANCE below.

import requests, json, time

# CONFIG — REPLACE THESE
TENANT_ID = "<your-tenant-id>"
CLIENT_ID = "<your-service-principal-client-id>"
CLIENT_SECRET = "<your-service-principal-client-secret>"
DATABRICKS_INSTANCE = "https://<your-instance>.azuredatabricks.net"  # e.g. https://adb-12345.7.azuredatabricks.net

# Endpoint names from your screenshot
ENDPOINTS = ["gpt41mini", "gpt-41", "gpt-4o"]

# Simple prompt payload for text LLMs
PROMPT = "Answer concisely: What is retrieval-augmented generation (RAG)?"

def get_azure_ad_token(tenant, cid, secret):
    url = f"https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": secret,
        "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default"
    }
    r = requests.post(url, data=data, headers={"Content-Type":"application/x-www-form-urlencoded"})
    r.raise_for_status()
    return r.json()["access_token"]

def create_db_token(db_instance, aad_token):
    url = f"{db_instance.rstrip('/')}/api/2.0/token/create"
    r = requests.post(url, headers={"Authorization": f"Bearer {aad_token}", "Content-Type":"application/json"},
                      json={"comment":"SP-created token for quick model tests"})
    r.raise_for_status()
    j = r.json()
    # token_value field contains the token
    token = j.get("token_value") or (j.get("token") or {}).get("value")
    if not token:
        raise RuntimeError("Databricks token not returned: " + json.dumps(j))
    return token

def call_endpoint(db_instance, db_token, endpoint_name, prompt):
    url = f"{db_instance.rstrip('/')}/serving-endpoints/{endpoint_name}/invocations"
    payload = {"inputs": [{"text": prompt}]}
    r = requests.post(url, headers={"Authorization": f"Bearer {db_token}", "Content-Type":"application/json"}, json=payload, timeout=120)
    return r

# --- Main ---
try:
    print("Obtaining Azure AD token...")
    aad = get_azure_ad_token(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
    print("Exchanging for Databricks token...")
    db_token = create_db_token(DATABRICKS_INSTANCE, aad)
    print("Databricks token acquired (short-lived).")
except Exception as e:
    raise SystemExit("Auth failed: " + str(e))

for name in ENDPOINTS:
    print(f"\nCalling endpoint: {name}")
    try:
        resp = call_endpoint(DATABRICKS_INSTANCE, db_token, name, PROMPT)
        print("HTTP", resp.status_code)
        ctype = resp.headers.get("Content-Type","")
        if resp.status_code == 200:
            if "application/json" in ctype:
                print(json.dumps(resp.json(), indent=2))
            else:
                print(resp.text)
        else:
            print("Error body:", resp.text)
    except Exception as e:
        print("Call failed:", str(e))
    time.sleep(0.5)

print("\nDone. Revoke the created Databricks token in the workspace UI if you don't need it.")
