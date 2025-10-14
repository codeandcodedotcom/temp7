from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ServeEndpointRequest
import os

# ===== HARDCODED VALUES =====
# Set these environment variables in your Databricks cluster or notebook
WORKSPACE_URL = "https://adb-<workspace-id>.azuredatabricks.net"  # Replace with your workspace URL
CLIENT_ID = "your-client-id-here"                                  # Replace with Service Principal App ID
CLIENT_SECRET = "your-client-secret-here"                          # Replace with Service Principal secret
TENANT_ID = "your-tenant-id-here"                                  # Replace with Azure Tenant ID

# Models to test
MODELS = ["gpt-4-1-mini", "gpt-4-1", "gpt-4o"]

# ===== Initialize Databricks Client using Service Principal =====
try:
    client = WorkspaceClient(
        host=WORKSPACE_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        azure_tenant_id=TENANT_ID
    )
    print("✓ Databricks authentication successful\n")
except Exception as e:
    print(f"✗ Authentication failed: {str(e)}")
    exit()

# ===== Test Model Accessibility =====
print(f"Testing models: {MODELS}\n")

for model in MODELS:
    try:
        endpoint = client.serving_endpoints.get(model)
        print(f"✓ {model}: Accessible")
        print(f"  Status: {endpoint.state}")
    except Exception as e:
        if "404" in str(e) or "not found" in str(e).lower():
            print(f"✗ {model}: Not found")
        else:
            print(f"✗ {model}: {str(e)}")
