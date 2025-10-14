from databricks.sdk import WorkspaceClient

# ===== HARDCODED VALUES =====
# Set these with your actual values
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
        # Using get method directly on serving_endpoints
        endpoint = client.serving_endpoints.get(model)
        print(f"✓ {model}: Accessible")
        print(f"  Status: {endpoint.state}")
    except Exception as e:
        error_str = str(e).lower()
        if "404" in str(e) or "not found" in error_str:
            print(f"✗ {model}: Not found (404)")
        elif "403" in str(e) or "forbidden" in error_str:
            print(f"✗ {model}: Forbidden - No permission (403)")
        else:
            print(f"✗ {model}: Error - {str(e)}")
