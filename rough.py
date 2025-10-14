import requests
import json

# ===== HARDCODED VALUES - Replace with your actual values =====
# Get these from Azure Databricks:
# 1. WORKSPACE_URL: https://<region>.azuredatabricks.net (found in your Databricks workspace URL bar)
# 2. CLIENT_ID: Service Principal App ID (from Azure Entra ID / Service Principal)
# 3. CLIENT_SECRET: Service Principal password/secret (from Azure Entra ID / Service Principal)
# 4. TENANT_ID: Azure Tenant ID (from Azure Entra ID / Overview / Tenant ID)

WORKSPACE_URL = "https://adb-<workspace-id>.azuredatabricks.net"  # Replace with your workspace URL
CLIENT_ID = "your-client-id-here"                                  # Replace with your Service Principal App ID
CLIENT_SECRET = "your-client-secret-here"                          # Replace with your Service Principal secret
TENANT_ID = "your-tenant-id-here"                                  # Replace with your Azure Tenant ID

# Models to test
MODELS = ["gpt-4-1-mini", "gpt-4-1", "gpt-4o"]

# ===== STEP 1: Get Azure Token =====
token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
token_data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default",  # Databricks API scope
    "grant_type": "client_credentials"
}

token_response = requests.post(token_url, data=token_data)
if token_response.status_code != 200:
    print(f"Failed to get token: {token_response.text}")
    exit()

access_token = token_response.json()["access_token"]
print("✓ Azure authentication successful\n")

# ===== STEP 2: Test Model Accessibility =====
print(f"Testing models: {MODELS}\n")

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

for model in MODELS:
    url = f"{WORKSPACE_URL}/api/2.0/serving-endpoints/{model}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print(f"✓ {model}: Accessible")
        elif response.status_code == 404:
            print(f"✗ {model}: Not found (404)")
        else:
            print(f"✗ {model}: Error {response.status_code}")
    except Exception as e:
        print(f"✗ {model}: {str(e)}")
